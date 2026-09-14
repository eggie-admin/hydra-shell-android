class_name RelicPckProbe
extends RefCounted

static func probe(path: String) -> Dictionary:
	var out := {"path": path, "kind": "unknown", "magic": "", "size": 0}
	if not FileAccess.file_exists(path):
		out["kind"] = "missing"
		return out
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		out["kind"] = "unreadable"
		return out
	out["size"] = f.get_length()
	var bytes := f.get_buffer(mini(16, f.get_length()))
	var magic := ""
	for b in bytes:
		if b >= 32 and b <= 126:
			magic += char(b)
		else:
			magic += "."
	out["magic"] = magic
	if bytes.size() >= 4 and bytes[0] == 0x50 and bytes[1] == 0x43 and bytes[2] == 0x4b and bytes[3] == 0x00:
		out["kind"] = "legacy_pck"
	return out
