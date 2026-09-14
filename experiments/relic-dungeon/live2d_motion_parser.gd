class_name LegacyLive2DMotion
extends RefCounted

var fps: float = 30.0
var fade_in_ms: float = 0.0
var fade_out_ms: float = 0.0
var tracks: Dictionary = {}
var frame_count: int = 1

func load_file(path: String) -> bool:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return false
	return parse_text(f.get_as_text())

func parse_text(text: String) -> bool:
	tracks.clear()
	frame_count = 1
	text = text.replace("\r\n", "\n").replace("\r", "\n")
	for raw in text.split("\n"):
		var line := raw.strip_edges()
		if line.is_empty() or line.begins_with("#"):
			continue
		if line.begins_with("$"):
			var meta := line.substr(1).split("=", true, 1)
			if meta.size() != 2:
				continue
			match String(meta[0]).to_lower():
				"fps": fps = maxf(1.0, float(meta[1]))
				"fadein": fade_in_ms = float(meta[1])
				"fadeout": fade_out_ms = float(meta[1])
			continue

		var pair := line.split("=", true, 1)
		if pair.size() != 2:
			continue
		var key := String(pair[0]).strip_edges()
		var vals: Array[float] = []
		for token in String(pair[1]).split(","):
			var clean := token.strip_edges()
			if clean.is_empty():
				continue
			vals.append(float(clean))
		if vals.is_empty():
			continue
		tracks[key] = vals
		frame_count = maxi(frame_count, vals.size())
	return not tracks.is_empty()

func duration() -> float:
	return float(maxi(frame_count - 1, 1)) / fps

func sample(track: String, seconds: float, looped := true) -> float:
	if not tracks.has(track):
		return 0.0
	var values: Array = tracks[track]
	if values.size() == 1:
		return float(values[0])
	var dur := duration()
	var t := seconds
	if looped and dur > 0.0:
		t = fmod(maxf(t, 0.0), dur)
	else:
		t = clampf(t, 0.0, dur)
	var frame := t * fps
	var i0 := clampi(int(floor(frame)), 0, values.size() - 1)
	var i1 := clampi(i0 + 1, 0, values.size() - 1)
	var a := frame - float(i0)
	return lerpf(float(values[i0]), float(values[i1]), a)

func summary() -> Dictionary:
	return {
		"fps": fps,
		"fade_in_ms": fade_in_ms,
		"fade_out_ms": fade_out_ms,
		"frame_count": frame_count,
		"duration": duration(),
		"track_count": tracks.size()
	}
