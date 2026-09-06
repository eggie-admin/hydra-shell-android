/* KAI9000 jQuery cockpit. Browser is UI only; policy lives in Python. */
(function ($) {
  "use strict";

  function show(payload) {
    $("#out").text(typeof payload === "string" ? payload : JSON.stringify(payload, null, 2));
  }

  function api(method, path, body) {
    return $.ajax({
      url: path,
      method: method,
      contentType: "application/json",
      dataType: "json",
      data: body === undefined ? undefined : JSON.stringify(body)
    }).done(show).fail(function (xhr) {
      var payload = xhr.responseJSON || {error: xhr.statusText, status: xhr.status};
      show(payload);
    });
  }

  function post(path, body) {
    return api("POST", path, body);
  }

  function numericOrNull(value) {
    return value === "" ? null : Number(value);
  }

  function refreshSpells() {
    api("GET", "/api/magic/spells").done(function (data) {
      var $list = $("#spellList").empty();
      $.each(data.spells || {}, function (name, spec) {
        var approval = spec.approval ? " approval" : " auto";
        $("<option>").val(name).text(name + " · " + spec.school + " · R" + spec.rank + " · " + spec.mp + " MP ·" + approval).appendTo($list);
      });
      $("#codeRoot").text(data.code_root || "");
    });
  }

  function selectedArgs() {
    var raw = $("#spellArgs").val().trim();
    if (!raw) { return {}; }
    try { return JSON.parse(raw); }
    catch (err) { throw new Error("Spell args must be valid JSON"); }
  }

  $(function () {
    refreshSpells();

    $("#askOpenAI").on("click", function () {
      post("/api/magic/chat", {message: $("#magicPrompt").val()});
    });

    $("#prepareCast").on("click", function () {
      try {
        post("/api/magic/cast/prepare", {spell: $("#spellList").val(), args: selectedArgs()}).done(function (data) {
          $("#castId").val(data.cast_id || "");
          $("#approvalState").text(data.approved ? "AUTO-APPROVED" : "APPROVAL REQUIRED");
        });
      } catch (err) {
        show({error: err.message});
      }
    });

    $("#approveCast").on("click", function () {
      var id = $("#castId").val().trim();
      if (!id) { return show({error: "Prepare a cast first"}); }
      post("/api/magic/cast/" + encodeURIComponent(id) + "/approve", {approved: true}).done(function () {
        $("#approvalState").text("APPROVED");
      });
    });

    $("#executeCast").on("click", function () {
      var id = $("#castId").val().trim();
      if (!id) { return show({error: "Prepare a cast first"}); }
      post("/api/magic/cast/" + encodeURIComponent(id) + "/execute", {});
    });

    $("#rollbackCast").on("click", function () {
      var id = $("#castId").val().trim();
      if (!id) { return show({error: "Checkpoint cast ID required"}); }
      post("/api/magic/cast/" + encodeURIComponent(id) + "/rollback", {approved: true});
    });

    $("#demux").on("click", function () {
      post("/api/demux", {source_mp4: $("#src").val(), label: $("#label").val()}).done(function (data) {
        if (data.job_id) { $("#job").val(data.job_id); }
      });
    });

    $(".apng").on("click", function () {
      var ai = $(this).data("ai") === true || $(this).data("ai") === "true";
      post("/api/apng", {job_id: $("#job").val(), use_ai_frames: ai, fps: 12, loop: 0}).done(function (data) {
        if (data.download) { $("#apngImage").attr("src", data.download + "?t=" + Date.now()); }
      });
    });

    $("#remux").on("click", function () {
      post("/api/remux", {job_id: $("#job").val(), use_ai_frames: true, crf: 18, preset: "medium"}).done(function (data) {
        if (data.download) { $("#mp4").attr("src", data.download + "?t=" + Date.now()); }
      });
    });

    $("#regen").on("click", function () {
      post("/api/comfy/regen", {
        job_id: $("#job").val(),
        start_frame: numericOrNull($("#start").val()),
        end_frame: numericOrNull($("#end").val()),
        step: Number($("#step").val() || 1),
        timeout_s: 900
      });
    });

    $("#seal").on("click", function () {
      post("/api/seal", {job_id: $("#job").val(), include_source_mp4: false});
    });

    $("#backup").on("click", function () {
      post("/api/backup", {job_id: $("#job").val(), include_source_mp4: false});
    });

    $("#askOllama").on("click", function () {
      post("/api/antenna/ollama/chat", {message: $("#ollamaPrompt").val()});
    });
  });
})(window.jQuery);
