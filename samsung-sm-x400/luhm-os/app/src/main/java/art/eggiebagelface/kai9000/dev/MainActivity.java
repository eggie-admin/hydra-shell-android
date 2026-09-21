package art.eggiebagelface.kai9000.dev;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.pm.ApplicationInfo;
import android.os.Bundle;
import android.os.IBinder;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.webkit.WebViewAssetLoader;

public final class MainActivity extends Activity {
    private WebView webView;
    private EngineService engine;
    private boolean bound;

    private final ServiceConnection engineConnection = new ServiceConnection() {
        @Override public void onServiceConnected(ComponentName name, IBinder service) {
            engine = ((EngineService.LocalBinder) service).engine();
            bound = true;
            notifyEngineReady();
        }
        @Override public void onServiceDisconnected(ComponentName name) {
            bound = false;
            engine = null;
        }
    };

    @SuppressLint("SetJavaScriptEnabled")
    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        bindService(new Intent(this, EngineService.class), engineConnection, Context.BIND_AUTO_CREATE);

        WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        webView = new WebView(this);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(false);
        webView.getSettings().setAllowFileAccess(false);
        webView.getSettings().setAllowContentAccess(false);
        webView.getSettings().setJavaScriptCanOpenWindowsAutomatically(false);
        webView.getSettings().setSupportMultipleWindows(false);
        WebView.setWebContentsDebuggingEnabled((getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0);
        webView.addJavascriptInterface(new LuhmBridge(), "LUHM");
        webView.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return loader.shouldInterceptRequest(request.getUrl());
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return !"appassets.androidplatform.net".equals(request.getUrl().getHost());
            }
        });
        setContentView(webView);
        webView.loadUrl("https://appassets.androidplatform.net/assets/index.html");
    }

    private void notifyEngineReady() {
        if (webView != null) webView.post(() -> webView.evaluateJavascript("window.LUHMEngineReady && window.LUHMEngineReady()", null));
    }

    @Override protected void onDestroy() {
        if (bound) unbindService(engineConnection);
        if (webView != null) {
            webView.removeJavascriptInterface("LUHM");
            webView.destroy();
        }
        super.onDestroy();
    }

    private final class LuhmBridge {
        @JavascriptInterface public String platform() {
            return "{\"app\":\"LuHm OS\",\"package\":\"" + getPackageName()
                    + "\",\"deviceTarget\":\"SM-X400\",\"targetApi\":37,"
                    + "\"installModel\":\"single-standard-android-apk\","
                    + "\"termuxRequired\":false,\"bashInstallerRequired\":false,"
                    + "\"networkPermission\":false}";
        }
        @JavascriptInterface public String engineStatus() {
            return bound && engine != null ? engine.status() : "{\"engine\":\"binding\",\"ok\":false}";
        }
        @JavascriptInterface public String runTyped(String action) {
            return bound && engine != null ? engine.runTyped(action) : "{\"ok\":false,\"error\":\"ENGINE_NOT_BOUND\"}";
        }
    }
}
