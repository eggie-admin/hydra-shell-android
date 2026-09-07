/* KAI9000 jQuery cockpit. Browser is UI only; policy lives in Python. */
(function ($) {
  "use strict";

  var SESSION_KEY = "kai9000.lum.session.v1";

  function show(payload) {
    $("#out").text(typeof payload === "string" ? payload : JSON.stringify(payload, null, 2));
  }

  function api(method, path, body, quiet) {
    var req = $.ajax({
      url: path,
      method: method,
      contentType: "application/json",
      dataType: "json",
      data: body === undefined ? undefined : JSON.stringify(body)
    });
    if (!quiet) { req.done(show); }
    req.fail(function (xhr) {
      var payload = xhr.responseJSON || {error: xhr.statusText, status: xhr.status};
      show(payload);
    });
    return req;
  }

  function post(path, body, quiet) {
    return api("POST", path, body, quiet);
  }

  function numericOrNull(value) {
    return value === "" ? null : Number(value);
  }

  function newSessionId() {
    var tail;
    if (window.crypto && window.crypto.randomUUID) {
      tail = window.crypto.randomUUID().replace(/[^A-Za-z0-9_-]/g, "").slice(0, 32);
    } else {
      tail = Date.now().toString(36) + Math.random().toString(36).slice(2, 12);
    }
    return "kai-s24-" + tail;
  }

  function getSessionId() {
    var current = window.localStorage.getItem(SESSION_KEY);
    if (!current || !/^[A-Za-z0-9._-]{1,64}$/.test(current)) {
      current = newSessionId();
      window.localStorage.setItem(SESSION_KEY, current);
    }
    return current;
  }

  function setSessionLabel() {
    $("#lumSessionLabel").text(getSessionId());
  }

  function appendMessage(role, text) {
    var $msg = $("<div>").addClass("msg " + (role === "user" ? "user" : "lum"));
    $("<span>").addClass("who").text(role === "user" ? "Professor" : "Lum").appendTo($msg);
    $msg.append(document.createTextNode(text || ""));
    $("#lumChatLog").append($msg);
    var log = document.getElementById("lumChatLog");
    if (log) { log.scrollTop = log.scrollHeight; }
  }

  function resetChatView() {
    $("#lumChatLog").empty();
    appendMessage("lum", "New KAI 9000 session opened. Crown authority remains with Professor.");
    $("#lumRoute").text("route: waiting");
    setSessionLabel();
  }

  function refreshLumStatus() {
    api("GET", "/api/lum/status", undefined, true).done(function (data) {
      var state = data.credential_configured ? "OPENAI READY" : "DETERMINISTIC MOCK";
      $("#lumStatus").text(
        data.agent + " · " + data.default_model + " / " + data.heavy_model + " · " + data.transport + " · " + state
      );
      $("#providerChip").text("LUM: " + state);
      $("#lumRoute").text("route: " + data.default_model + " → " + data.heavy_model);
    });
  }

  function sendLumMessage(text) {
    var message = (text === undefined ? $("#magicPrompt").val() : text).trim();
    if (!message) { return; }
    appendMessage("user", message);
    $("#magicPrompt").val("").prop("disabled", true);
    $("#askOpenAI").prop("disabled", true).text("Casting…");

    post("/api/lum/chat", {message: message, session_id: getSessionId()}, true)
      .done(function (data) {
        appendMessage("lum", data.assistant || "No assistant text returned.");
        $("#lumRoute").text(
          "route: " + (data.route || "unknown") + " · " + (data.model || data.planned_model || "deterministic")
        );
        show(data);
      })
      .fail(function (xhr) {
        var detail = (xhr.responseJSON && xhr.responseJSON.detail) || xhr.statusText || "Lum request failed";
        appendMessage("lum", "RED: " + (typeof detail === "string" ? detail : JSON.stringify(detail)));
      })
      .always(function () {
        $("#magicPrompt").prop("disabled", false).focus();
        $("#askOpenAI").prop("disabled", false).text("Cast Message");
      });
  }

  function refreshSpells() {
    api("GET", "/api/magic/spells", undefined, true).done(function (data) {
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
    setSessionLabel();
    refreshLumStatus();
    refreshSpells();

    $("#askOpenAI").on("click", function () { sendLumMessage(); });

    $("#magicPrompt").on("keydown", function (event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendLumMessage();
      }
    });

    $("#newLumSession").on("click", function () {
      window.localStorage.setItem(SESSION_KEY, newSessionId());
      resetChatView();
    });

    $(".quickPrompt").on("click", function () {
      var prompt = String($(this).data("prompt") || "");
      $("#magicPrompt").val(prompt);
      sendLumMessage(prompt);
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
  });
})(window.jQuery);