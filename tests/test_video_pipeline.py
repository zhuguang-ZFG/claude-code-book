"""Consumer boundaries for the shared chapter video factory."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "video"))
from pipeline import captions, model, quality, timeline, voice


class TrackedVideoInventory(unittest.TestCase):
    def test_only_authored_sources_and_pipeline_code_are_tracked(self):
        result = subprocess.run(["git", "ls-files", "video"], cwd=ROOT,
                                capture_output=True, text=True, encoding="utf-8")
        if result.returncode:
            self.skipTest("git metadata is unavailable")
        tracked = [line for line in result.stdout.splitlines() if line]
        media = {".mp3", ".mp4", ".mov", ".webm", ".wav", ".m4a", ".aac",
                 ".png", ".jpg", ".jpeg", ".webp"}
        generated_names = ("vo-concat.txt", "short-meta.json", "chunks.json",
                           "vo-manifest", "transcript", "captions-")
        problems = []
        for path in tracked:
            suffix = Path(path).suffix.lower()
            name = Path(path).name
            if suffix in media:
                problems.append(f"media: {path}")
            elif suffix in {".srt", ".vtt"}:
                problems.append(f"captions: {path}")
            elif suffix == ".py" and not path.startswith("video/pipeline/"):
                problems.append(f"legacy script: {path}")
            elif name in generated_names or any(
                    name.startswith(prefix) for prefix in generated_names):
                problems.append(f"generated: {path}")
            elif "/assets/" in path and path.split("/assets/", 1)[0].split(
                    "/")[-1] in {"ch01", "ch02", "ch03", "ch04", "ch05"}:
                allowed = {
                    "video/ch01/assets/huashu/ch01-whiteboard.json",
                    "video/ch01/assets/sample-long.txt",
                    "video/ch01/assets/sample-short.txt",
                    "video/ch02/assets/sample-short.txt",
                    "video/ch03/assets/sample-short.txt",
                    "video/ch04/assets/sample-short.txt",
                    "video/ch05/assets/sample-short.txt",
                }
                if path not in allowed:
                    problems.append(f"intermediate: {path}")
        self.assertEqual(problems, [])


class ConfigurationBoundary(unittest.TestCase):
    def test_audio_gate_rejects_a_configuration_without_recordings(self):
        episode = {"id": "ch06", "formats": {
            name: {"status": "scripted", "width": width, "height": height,
                   "duration_s": 20}
            for name, (width, height) in model.FORMAT_SIZE.items()},
            "captions": dict(model.DEFAULT_CAPTIONS),
            "quality": dict(model.DEFAULT_QUALITY),
            "rights": {"owner": "original", "music": "none", "footage": "none"}}
        with tempfile.TemporaryDirectory() as directory:
            chapter = Path(directory) / "ch06"
            chapter.mkdir()
            self.assertEqual(quality.check(episode, {}, {}, {}, chapter), [])
            errors = quality.check(episode, {}, {}, {}, chapter, check_audio=True)
        self.assertEqual(errors, [
            "ch06: long narration is not declared; audio verification requires a real recording",
            "ch06: short narration is not declared; audio verification requires a real recording"])

    def test_audio_gate_rejects_an_unresolvable_recording_base(self):
        episode = {"id": "ch06", "formats": {"short": {
            "status": "scripted", "width": 1080, "height": 1920, "duration_s": 20}},
            "captions": dict(model.DEFAULT_CAPTIONS),
            "quality": dict(model.DEFAULT_QUALITY),
            "rights": {"owner": "original", "music": "none", "footage": "none"}}
        with tempfile.TemporaryDirectory() as directory:
            chapter = Path(directory) / "ch06"
            chapter.mkdir()
            errors = quality.check(episode, {"audio": {"short": {
                "path": "voice.mp3", "duration_s": 20}}}, {}, {}, chapter,
                check_audio=True)
        self.assertEqual(errors, [
            "ch06: short narration base cannot be resolved for voice.mp3"])

    def test_missing_media_is_explicitly_separate_from_config_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            chapter = Path(directory) / "ch01"
            chapter.mkdir()
            episode = {"formats": {"short": {"status": "built", "duration_s": 20}}}
            scenes = {"schema_version": 1, "episode": "ch01", "formats": {
                "short": [{"id": "opening", "start_s": 0, "duration_s": 20,
                           "source": "missing.html", "intent": "hook"}]},
                "audio": {"short": {"path": "missing.mp3", "duration_s": 20}}}
            episode["legacy"] = {"dir": ".", "short_index": "index.html"}
            self.assertEqual(model.validate_scenes(
                scenes, episode, chapter, check_assets=False), [])
            errors = model.validate_scenes(scenes, episode, chapter)
            self.assertTrue(any("composition missing.html is missing" in item
                                for item in errors), errors)
            self.assertTrue(any("audio missing.mp3 is missing" in item
                                for item in errors), errors)

    def test_scripted_timeline_contains_scenes_and_render_state(self):
        episode = {"id": "ch06", "formats": {"short": {
            "status": "scripted", "width": 1080, "height": 1920,
            "fps": 30, "duration_s": 20}}}
        scene = {"id": "hook", "start_s": 0, "duration_s": 20,
                 "source": "compositions/hook.html", "intent": "hook"}
        result = timeline.build(episode, {"formats": {"short": [scene]}}, {})
        self.assertEqual(result["formats"]["short"]["scenes"], [scene])
        self.assertEqual(result["formats"]["short"]["status"], "scripted")

    def test_asset_failure_is_a_named_cli_error_not_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chapter = root / "ch01"
            shutil.copytree(model.CHAPTERS / "ch01", chapter)
            episode = model.read_yaml(chapter / "episode.yaml")
            episode["legacy"]["dir"] = "../legacy"
            model.write_yaml(chapter / "episode.yaml", episode)
            for name in ("index.html", "short/index.html"):
                index = root / "legacy" / name
                index.parent.mkdir(parents=True, exist_ok=True)
                index.write_text("<!doctype html>", encoding="utf-8")
            bootstrap = (
                "import sys; from pathlib import Path; "
                "sys.path.insert(0, str(Path(sys.argv[1]) / 'video')); "
                "from pipeline import model, cli; "
                "model.CHAPTERS=Path(sys.argv[2]); "
                "raise SystemExit(cli.main(['check','--chapter','ch01']))")
            result = subprocess.run(
                [sys.executable, "-c", bootstrap, str(ROOT), str(root)],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertIn("VIDEO FAILED:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("audio full.mp3 is missing", result.stderr)


class RecordedCueTrack(unittest.TestCase):
    """Cues rebuilt from recorded subtitle assets reproduce the shipped track."""

    def _chapter(self, root: Path, script: str = "第一句。\n第二句。"):
        chapter = root / "chapters" / "ch01"
        chapter.mkdir(parents=True)
        (chapter / "script-long.txt").write_text(script, encoding="utf-8")
        (root / "ch01" / "hf-remake").mkdir(parents=True)
        episode = {
            "id": "ch01",
            "legacy": {"dir": "../../ch01/hf-remake", "long_index": "index.html"},
            "scripts": {"long": {"path": "script-long.txt", "mode": "paragraph"}},
            "formats": {"long": {"status": "built", "width": 1920, "height": 1080,
                                 "fps": 30, "duration_s": 10.0}},
        }
        return episode, chapter

    def _probe(self, durations: dict[str, float]):
        return mock.patch.object(
            voice, "_duration",
            side_effect=lambda path: durations.get(path.name, 3.0))

    def test_timeline_vtt_merge_shifts_by_recorded_start(self):
        with tempfile.TemporaryDirectory() as directory:
            episode, chapter = self._chapter(Path(directory))
            vo = Path(directory) / "ch01" / "assets" / "vo"
            (vo / "mp3").mkdir(parents=True)
            (vo / "mp3" / "01.mp3").write_bytes(b"mp3")
            (vo / "mp3" / "01.vtt").write_text(
                "WEBVTT\n\n00:00:00,500 --> 00:00:01,500\n第一句。\n\n"
                "00:00:01,500 --> 00:00:02,800\n第二句。\n",
                encoding="utf-8")
            (vo / "timeline.json").write_text(
                json.dumps([{"id": "01", "start": 2.5, "duration": 3.0}]),
                encoding="utf-8")
            with self._probe({"01.mp3": 3.0}):
                cues = voice.recorded_cues(episode, chapter, "long")
                self.assertEqual(voice.cue_source(episode, chapter, "long"),
                                 voice.RECORDED_TIMELINE)
                self.assertEqual(voice.cues(episode, chapter, "long"), cues)
            self.assertEqual(cues, [
                {"start": 3.0, "end": 4.0, "text": "第一句。"},
                {"start": 4.0, "end": 5.3, "text": "第二句。"},
            ])

    def test_missing_recording_asset_falls_back_to_estimates(self):
        with tempfile.TemporaryDirectory() as directory:
            episode, chapter = self._chapter(Path(directory))
            vo = Path(directory) / "ch01" / "assets" / "vo"
            (vo / "mp3").mkdir(parents=True)
            (vo / "mp3" / "01.vtt").write_text(
                "WEBVTT\n\n00:00:00,500 --> 00:00:01,500\n第一句。\n",
                encoding="utf-8")
            (vo / "timeline.json").write_text(
                json.dumps([{"id": "01", "start": 0.0, "duration": 3.0}]),
                encoding="utf-8")
            with self._probe({}):
                self.assertIsNone(voice.recorded_cues(episode, chapter, "long"))
                self.assertEqual(voice.cue_source(episode, chapter, "long"),
                                 "estimated")

    def test_vtt_cue_past_audio_end_is_not_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            episode, chapter = self._chapter(Path(directory))
            vo = Path(directory) / "ch01" / "assets" / "vo"
            (vo / "mp3").mkdir(parents=True)
            (vo / "mp3" / "01.mp3").write_bytes(b"mp3")
            (vo / "mp3" / "01.vtt").write_text(
                "WEBVTT\n\n00:00:00,500 --> 00:00:03,900\n第一句。\n",
                encoding="utf-8")
            (vo / "timeline.json").write_text(
                json.dumps([{"id": "01", "start": 0.0, "duration": 4.0}]),
                encoding="utf-8")
            with self._probe({"01.mp3": 3.0}):
                self.assertIsNone(voice.recorded_cues(episode, chapter, "long"))

    def test_transcript_json_absolute_timings(self):
        with tempfile.TemporaryDirectory() as directory:
            episode, chapter = self._chapter(Path(directory))
            base = Path(directory) / "ch01" / "hf-remake"
            (base / "short").mkdir(parents=True)
            (base / "transcript.json").write_text(
                json.dumps([{"text": "第一句。", "start": 0.08,
                             "end": 1.5, "id": "w0"}]),
                encoding="utf-8")
            cues = voice.recorded_cues(episode, chapter, "long")
            self.assertEqual(voice.cue_source(episode, chapter, "long"),
                             voice.RECORDED_TRANSCRIPT)
            self.assertEqual(cues,
                             [{"start": 0.08, "end": 1.5, "text": "第一句。"}])

    def test_short_caps_absolute_timings(self):
        with tempfile.TemporaryDirectory() as directory:
            episode, chapter = self._chapter(Path(directory))
            caps = (Path(directory) / "ch01" / "hf-remake" / "short"
                    / "assets")
            caps.mkdir(parents=True)
            (caps / "short-caps.json").write_text(
                json.dumps([{"start": 0.5, "end": 2.0, "text": "第一句。"}]),
                encoding="utf-8")
            episode["formats"]["short"] = {
                "status": "built", "width": 1080, "height": 1920,
                "fps": 30, "duration_s": 20.0}
            cues = voice.recorded_cues(episode, chapter, "short")
            self.assertEqual(voice.cue_source(episode, chapter, "short"),
                             voice.RECORDED_SHORT_CAPS)
            self.assertEqual(cues,
                             [{"start": 0.5, "end": 2.0, "text": "第一句。"}])

    def test_chunk_srt_merge_offsets_by_probed_durations(self):
        with tempfile.TemporaryDirectory() as directory:
            episode, chapter = self._chapter(Path(directory))
            vo = Path(directory) / "ch01" / "assets" / "vo"
            vo.mkdir(parents=True)
            for index in range(2):
                (vo / f"c{index:03d}.mp3").write_bytes(b"mp3")
                (vo / f"c{index:03d}.srt").write_text(
                    "1\n00:00:00,200 --> 00:00:01,000\n"
                    f"第{'一二'[index]}句。\n", encoding="utf-8")
            with self._probe({"c000.mp3": 2.0, "c001.mp3": 1.5}):
                cues = voice.recorded_cues(episode, chapter, "long")
                self.assertEqual(voice.cue_source(episode, chapter, "long"),
                                 voice.RECORDED_CHUNKS)
            self.assertEqual(cues, [
                {"start": 0.2, "end": 1.0, "text": "第一句。"},
                {"start": 2.2, "end": 3.0, "text": "第二句。"},
            ])


class KaraokeCaptions(unittest.TestCase):
    """The ported renderer regenerates the shipped caption page exactly."""

    SHIPPED_CH01_SHA256 = ("d8d0cc15cdb4ac4b40ecbfbe72dd22417e681f99"
                           "f533059531317e5491ae1630")

    def test_generator_renders_cue_tokens_and_timeline(self):
        body = captions.karaoke_captions_html(
            [{"start": 0.0, "end": 2.0, "text": "你好 AB。"}], 60.0)
        self.assertIn('data-duration="60.000"', body)
        self.assertIn('id="c0" class="cap-clip clip" data-start="0.100" '
                      'data-duration="1.900" data-track-index="10"', body)
        # CJK chars split alone; latin runs and trailing punctuation
        # (U+3002 is outside the CJK ranges) stay merged: "AB。".
        for kid in range(4):
            self.assertIn(f'id="c0-k{kid}"', body)
        self.assertNotIn('id="c0-k4"', body)
        self.assertIn('tl.to("#c0-in", {opacity:1, duration:0.10}, 0.100);',
                      body)
        self.assertIn('tl.to("#c0-in", {opacity:0, duration:0.12}, 1.880);',
                      body)

    def test_watermark_is_static_brand_page(self):
        body = captions.watermark_html(60.0)
        self.assertIn('data-composition-id="watermark"', body)
        self.assertIn("小电讲电路", body)
        self.assertIn('tl.set("#wm", {opacity:0.70}, 0);', body)

    def test_ch01_generated_captions_match_shipped_witness(self):
        import hashlib
        chapter_dir = model.CHAPTERS / "ch01"
        timeline_path = chapter_dir / "../../ch01/assets/vo/timeline.json"
        if not timeline_path.resolve().is_file():
            self.skipTest("recorded ch01 assets are not on this machine")
        episode = model.read_yaml(chapter_dir / "episode.yaml")
        cues = voice.recorded_cues(episode, chapter_dir, "long")
        self.assertIsNotNone(cues)
        body = captions.karaoke_captions_html(
            cues, episode["formats"]["long"]["duration_s"])
        shipped = body.replace("\n", "\r\n").encode("utf-8")
        self.assertEqual(hashlib.sha256(shipped).hexdigest(),
                         self.SHIPPED_CH01_SHA256)


if __name__ == "__main__":
    unittest.main()
