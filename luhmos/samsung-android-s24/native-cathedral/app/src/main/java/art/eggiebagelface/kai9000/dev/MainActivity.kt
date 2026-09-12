package art.eggiebagelface.kai9000.dev

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.webkit.WebViewAssetLoader
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private val executor = Executors.newSingleThreadExecutor()

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = Color.BLACK
        window.navigationBarColor = Color.BLACK

        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        webView = WebView(this).apply {
            setBackgroundColor(Color.TRANSPARENT)
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = false
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.javaScriptCanOpenWindowsAutomatically = false
            settings.setSupportMultipleWindows(false)
            WebView.setWebContentsDebuggingEnabled(true)
            webViewClient = object : WebViewClient() {
                override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest): WebResourceResponse? =
                    loader.shouldInterceptRequest(request.url)
            }
            addJavascriptInterface(KaiBridge(this@MainActivity, this, executor), "KAI9000")
        }
        setContentView(webView)
        webView.loadUrl("https://appassets.androidplatform.net/assets/cathedral/index.html")
    }

    override fun onDestroy() {
        webView.removeJavascriptInterface("KAI9000")
        webView.destroy()
        executor.shutdownNow()
        super.onDestroy()
    }
}

private class KaiBridge(
    private val context: Context,
    private val webView: WebView,
    private val executor: java.util.concurrent.ExecutorService
) {
    @JavascriptInterface
    fun platform(): String = JSONObject()
        .put("shell", "native-android-webview")
        .put("package", context.packageName)
        .put("edgeGallery", edgeAvailable())
        .put("ollama", "http://127.0.0.1:11434")
        .toString()

    @JavascriptInterface
    fun edgeAvailable(): Boolean =
        context.packageManager.getLaunchIntentForPackage("com.google.aiedge.gallery") != null

    @JavascriptInterface
    fun openEdgeGallery(): Boolean {
        val intent = context.packageManager.getLaunchIntentForPackage("com.google.aiedge.gallery") ?: return false
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
        return true
    }

    @JavascriptInterface
    fun probeOllama(): String {
        val requestId = UUID.randomUUID().toString()
        executor.execute {
            var connection: HttpURLConnection? = null
            try {
                connection = URL("http://127.0.0.1:11434/api/tags").openConnection() as HttpURLConnection
                connection.connectTimeout = 900
                connection.readTimeout = 1400
                connection.requestMethod = "GET"
                val ok = connection.responseCode in 200..299
                callback(JSONObject().put("kind", "status").put("requestId", requestId).put("provider", "ollama").put("ok", ok))
            } catch (t: Throwable) {
                callback(JSONObject().put("kind", "status").put("requestId", requestId).put("provider", "ollama").put("ok", false).put("error", t.javaClass.simpleName))
            } finally {
                connection?.disconnect()
            }
        }
        return requestId
    }

    @JavascriptInterface
    fun ollamaChat(prompt: String, model: String): String {
        val requestId = UUID.randomUUID().toString()
        val safeModel = model.trim().ifEmpty { "gemma3:1b" }
        val safePrompt = prompt.take(4000)
        executor.execute {
            var connection: HttpURLConnection? = null
            try {
                val body = JSONObject()
                    .put("model", safeModel)
                    .put("stream", false)
                    .put("messages", JSONArray().put(JSONObject().put("role", "user").put("content", safePrompt)))
                    .toString()
                connection = URL("http://127.0.0.1:11434/api/chat").openConnection() as HttpURLConnection
                connection.connectTimeout = 1800
                connection.readTimeout = 60000
                connection.requestMethod = "POST"
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json")
                connection.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
                val code = connection.responseCode
                val stream = if (code in 200..299) connection.inputStream else connection.errorStream
                val raw = stream.bufferedReader().use { it.readText() }
                if (code !in 200..299) error("Ollama HTTP $code")
                val text = JSONObject(raw).optJSONObject("message")?.optString("content").orEmpty()
                callback(JSONObject().put("kind", "chat").put("requestId", requestId).put("provider", "ollama").put("ok", true).put("text", text))
            } catch (t: Throwable) {
                callback(JSONObject().put("kind", "chat").put("requestId", requestId).put("provider", "ollama").put("ok", false).put("error", t.message ?: t.javaClass.simpleName))
            } finally {
                connection?.disconnect()
            }
        }
        return requestId
    }

    private fun callback(payload: JSONObject) {
        webView.post { webView.evaluateJavascript("window.KAI9000Receive && window.KAI9000Receive(${payload});", null) }
    }
}
