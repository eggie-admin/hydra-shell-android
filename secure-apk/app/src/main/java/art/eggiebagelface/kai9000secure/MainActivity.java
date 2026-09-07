package art.eggiebagelface.kai9000secure;

import android.Manifest;
import android.app.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.graphics.Typeface;
import android.os.*;
import android.widget.*;

import java.io.*;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;

import javax.net.ssl.HttpsURLConnection;

public final class MainActivity extends Activity {
    private TextView status;

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildUi();

        if (Build.VERSION.SDK_INT >= 33 &&
            checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 9000);
        }
    }

    @Override protected void onStart() {
        super.onStart();
        startBackend();
        refreshStatus();
    }

    private void buildUi() {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(48, 64, 48, 48);

        TextView title = new TextView(this);
        title.setText("KAI 9000 SECURE");
        title.setTextSize(28);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        box.addView(title);

        TextView doctrine = new TextView(this);
        doctrine.setText("\nOne APK • HTTPS localhost • Android Keystore TLS • SQLite\nSecure Folder owns the identity and app data.\n");
        doctrine.setTextSize(16);
        box.addView(doctrine);

        status = new TextView(this);
        status.setText("Checking https://127.0.0.1:8443...");
        status.setTextSize(16);
        status.setTextIsSelectable(true);
        box.addView(status);

        Button start = new Button(this);
        start.setText("START BACKEND");
        start.setOnClickListener(v -> { startBackend(); refreshStatus(); });
        box.addView(start);

        Button stop = new Button(this);
        stop.setText("STOP BACKEND");
        stop.setOnClickListener(v -> {
            Intent i = new Intent(this, KaiBackendService.class).setAction(KaiBackendService.ACTION_STOP);
            startService(i);
            status.setText("STOP requested.");
        });
        box.addView(stop);

        Button refresh = new Button(this);
        refresh.setText("HTTPS HEALTH CHECK");
        refresh.setOnClickListener(v -> refreshStatus());
        box.addView(refresh);

        setContentView(box);
    }

    private void startBackend() {
        Intent i = new Intent(this, KaiBackendService.class).setAction(KaiBackendService.ACTION_START);
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(i);
        else startService(i);
    }

    private void refreshStatus() {
        status.setText("Checking TLS localhost...");
        Executors.newSingleThreadExecutor().execute(() -> {
            String result;
            try {
                Thread.sleep(250L);
                HttpsURLConnection c = (HttpsURLConnection) new URL("https://127.0.0.1:8443/api/health").openConnection();
                c.setSSLSocketFactory(LocalTls.pinnedClientSocketFactory());
                c.setHostnameVerifier((hostname, session) -> "127.0.0.1".equals(hostname) || "localhost".equalsIgnoreCase(hostname));
                c.setConnectTimeout(2000);
                c.setReadTimeout(2000);
                c.setUseCaches(false);
                int code = c.getResponseCode();
                try (InputStream in = code >= 400 ? c.getErrorStream() : c.getInputStream()) {
                    result = code + " " + readUtf8(in);
                }
                c.disconnect();
            } catch (Exception e) {
                result = "OFFLINE: " + e.getClass().getSimpleName() + ": " + e.getMessage();
            }
            String finalResult = result;
            runOnUiThread(() -> status.setText(finalResult));
        });
    }

    private static String readUtf8(InputStream in) throws IOException {
        if (in == null) return "";
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buffer = new byte[4096];
        int n;
        while ((n = in.read(buffer)) != -1) out.write(buffer, 0, n);
        return new String(out.toByteArray(), StandardCharsets.UTF_8);
    }
}
