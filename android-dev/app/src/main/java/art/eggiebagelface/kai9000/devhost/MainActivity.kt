package art.eggiebagelface.kai9000.devhost

import android.app.Activity
import android.graphics.Color
import android.os.Bundle
import android.view.ViewGroup
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private lateinit var status: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.BLACK)
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT,
            )
        }

        status = TextView(this).apply {
            text = "KAI 9000 native Android dev host • owner-profile cockpit"
            setTextColor(Color.WHITE)
            setPadding(24, 18, 24, 18)
        }

        val buttons = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
        }

        fun addButton(label: String, url: String) {
            buttons.addView(Button(this).apply {
                text = label
                setOnClickListener { loadLoopback(url) }
            }, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        }

        addButton("AcodeX", "http://127.0.0.1:8767/")
        addButton("VNC", "http://127.0.0.1:6080/vnc.html")

        webView = WebView(this).apply {
            setBackgroundColor(Color.BLACK)
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.safeBrowsingEnabled = true
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                    val host = request?.url?.host ?: return true
                    return host != "127.0.0.1" && host != "localhost"
                }

                override fun onPageFinished(view: WebView?, url: String?) {
                    status.text = "KAI 9000 Android dev host • ${url ?: "ready"}"
                }
            }
        }

        root.addView(status)
        root.addView(buttons)
        root.addView(webView, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            0,
            1f,
        ))
        setContentView(root)
        loadLoopback("http://127.0.0.1:8767/")
    }

    private fun loadLoopback(url: String) {
        status.text = "Connecting: $url"
        webView.loadUrl(url)
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (::webView.isInitialized && webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    override fun onDestroy() {
        if (::webView.isInitialized) {
            webView.stopLoading()
            webView.destroy()
        }
        super.onDestroy()
    }
}
