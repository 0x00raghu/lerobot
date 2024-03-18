from pathlib import Path
from typing import Sequence

import torch
from tensordict import TensorDictBase
from tensordict.nn import dispatch
from tensordict.utils import NestedKey
from torchaudio.io import StreamReader
from torchrl.envs.transforms import Transform


class ViewSliceHorizonTransform(Transform):
    invertible = False

    def __init__(self, num_slices, horizon):
        super().__init__()
        self.num_slices = num_slices
        self.horizon = horizon

    def _reset(self, tensordict: TensorDictBase, tensordict_reset: TensorDictBase) -> TensorDictBase:
        # _reset is called once when the environment reset to normalize the first observation
        tensordict_reset = self._call(tensordict_reset)
        return tensordict_reset

    @dispatch(source="in_keys", dest="out_keys")
    def forward(self, tensordict: TensorDictBase) -> TensorDictBase:
        return self._call(tensordict)

    def _call(self, td: TensorDictBase) -> TensorDictBase:
        td = td.view(self.num_slices, self.horizon)
        return td


class KeepFrames(Transform):
    invertible = False

    def __init__(
        self,
        positions,
        in_keys: Sequence[NestedKey],
        out_keys: Sequence[NestedKey] = None,
    ):
        if isinstance(positions, list):
            assert isinstance(positions[0], int)
        # TODO(rcadene)L add support for `isinstance(positions, int)`?

        self.positions = positions
        if out_keys is None:
            out_keys = in_keys
        super().__init__(in_keys=in_keys, out_keys=out_keys)

    def _reset(self, tensordict: TensorDictBase, tensordict_reset: TensorDictBase) -> TensorDictBase:
        # _reset is called once when the environment reset to normalize the first observation
        tensordict_reset = self._call(tensordict_reset)
        return tensordict_reset

    @dispatch(source="in_keys", dest="out_keys")
    def forward(self, tensordict: TensorDictBase) -> TensorDictBase:
        return self._call(tensordict)

    def _call(self, td: TensorDictBase) -> TensorDictBase:
        # we need set batch_size=[] before assigning a different shape to td[outkey]
        td.batch_size = []

        for inkey, outkey in zip(self.in_keys, self.out_keys, strict=False):
            # TODO(rcadene): don't know how to do `inkey not in td`
            if td.get(inkey, None) is None:
                continue
            td[outkey] = td[inkey][:, self.positions]
        return td


class DecodeVideoTransform(Transform):
    invertible = False

    def __init__(
        self,
        data_dir: Path | str,
        device="cpu",
        # format options are None=yuv420p (usually), rgb24, bgr24, etc.
        format: str | None = None,
        frame_rate: int | None = None,
        width: int | None = None,
        height: int | None = None,
        in_keys: Sequence[NestedKey] = None,
        out_keys: Sequence[NestedKey] = None,
        in_keys_inv: Sequence[NestedKey] | None = None,
        out_keys_inv: Sequence[NestedKey] | None = None,
    ):
        self.data_dir = Path(data_dir)
        self.device = device
        self.format = format
        self.frame_rate = frame_rate
        self.width = width
        self.height = height
        self.video_id_to_path = None
        if out_keys is None:
            out_keys = in_keys
        if in_keys_inv is None:
            in_keys_inv = out_keys
        if out_keys_inv is None:
            out_keys_inv = in_keys
        super().__init__(
            in_keys=in_keys, out_keys=out_keys, in_keys_inv=in_keys_inv, out_keys_inv=out_keys_inv
        )

    def set_video_id_to_path(self, video_id_to_path):
        self.video_id_to_path = video_id_to_path

    def _reset(self, tensordict: TensorDictBase, tensordict_reset: TensorDictBase) -> TensorDictBase:
        # _reset is called once when the environment reset to normalize the first observation
        tensordict_reset = self._call(tensordict_reset)
        return tensordict_reset

    @dispatch(source="in_keys", dest="out_keys")
    def forward(self, tensordict: TensorDictBase) -> TensorDictBase:
        return self._call(tensordict)

    def _call(self, td: TensorDictBase) -> TensorDictBase:
        assert (
            self.video_id_to_path is not None
        ), "Setting a video_id_to_path dictionary with `self.set_video_id_to_path(video_id_to_path)` is required."

        for inkey, outkey in zip(self.in_keys, self.out_keys, strict=False):
            # TODO(rcadene): don't know how to do `inkey not in td`
            if td.get(inkey, None) is None:
                continue

            bsize = len(td[inkey])  # num episodes in the batch
            b_frames = []
            for i in range(bsize):
                assert (
                    td["observation", "frame", "video_id"].ndim == 3
                    and td["observation", "frame", "video_id"].shape[2] == 1
                ), "We expect 2 dims. Respectively, number of episodes in the batch, number of observations, 1"

                ep_video_ids = td[inkey]["video_id"][i]
                timestamps = td[inkey]["timestamp"][i]
                frame_ids = td["frame_id"][i]

                unique_video_id = (ep_video_ids.min() == ep_video_ids.max()).item()
                assert unique_video_id

                is_ascending = torch.all(timestamps[:-1] <= timestamps[1:]).item()
                assert is_ascending

                is_contiguous = ((frame_ids[1:] - frame_ids[:-1]) == 1).all().item()
                assert is_contiguous

                FIRST_FRAME = 0  # noqa: N806
                video_id = ep_video_ids[FIRST_FRAME].squeeze(0).item()
                video_path = self.data_dir / self.video_id_to_path[video_id]
                first_frame_ts = timestamps[FIRST_FRAME].squeeze(0).item()
                num_contiguous_frames = len(timestamps)

                filter_desc = []
                video_stream_kwgs = {
                    "frames_per_chunk": num_contiguous_frames,
                    "buffer_chunk_size": num_contiguous_frames,
                }

                # choice of decoder
                if self.device == "cuda":
                    video_stream_kwgs["hw_accel"] = "cuda"
                    video_stream_kwgs["decoder"] = "h264_cuvid"
                    # video_stream_kwgs["decoder"] = "hevc_cuvid"
                    # video_stream_kwgs["decoder"] = "av1_cuvid"
                    # video_stream_kwgs["decoder"] = "ffv1_cuvid"
                else:
                    video_stream_kwgs["decoder"] = "h264"
                    # video_stream_kwgs["decoder"] = "hevc"
                    # video_stream_kwgs["decoder"] = "av1"
                    # video_stream_kwgs["decoder"] = "ffv1"

                # resize
                resize_width = self.width is not None
                resize_height = self.height is not None
                if resize_width or resize_height:
                    if self.device == "cuda":
                        assert resize_width and resize_height
                        video_stream_kwgs["decoder_option"] = {"resize": f"{self.width}x{self.height}"}
                    else:
                        scales = []
                        if resize_width:
                            scales.append(f"width={self.width}")
                        if resize_height:
                            scales.append(f"height={self.height}")
                        filter_desc.append(f"scale={':'.join(scales)}")

                # choice of format
                if self.format is not None:
                    if self.device == "cuda":
                        # TODO(rcadene): rebuild ffmpeg with --enable-cuda-nvcc, --enable-cuvid, and --enable-libnpp
                        raise NotImplementedError()
                        # filter_desc = f"scale=format={self.format}"
                        # filter_desc = f"scale_cuda=format={self.format}"
                        # filter_desc = f"scale_npp=format={self.format}"
                    else:
                        filter_desc.append(f"format=pix_fmts={self.format}")

                # choice of frame rate
                if self.frame_rate is not None:
                    filter_desc.append(f"fps={self.frame_rate}")

                if len(filter_desc) > 0:
                    video_stream_kwgs["filter_desc"] = ",".join(filter_desc)

                # create a stream and load a certain number of frame at a certain frame rate
                # TODO(rcadene): make sure it's the most optimal way to do it
                # s = StreamReader(str(video_path).replace('.mp4','.mkv'))
                s = StreamReader(str(video_path))
                s.seek(first_frame_ts)
                s.add_video_stream(**video_stream_kwgs)
                s.fill_buffer()
                (frames,) = s.pop_chunks()

                b_frames.append(frames)

            td[outkey] = torch.stack(b_frames)

        if self.device == "cuda":
            # make sure we return a cuda tensor, since the frames can be unwillingly sent to cpu
            assert "cuda" in str(td[outkey].device), f"{td[outkey].device} instead of cuda"
        return td