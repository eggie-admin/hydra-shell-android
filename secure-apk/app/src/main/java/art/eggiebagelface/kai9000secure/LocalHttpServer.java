package art.eggiebagelface.kai9000secure;

import android.content.Context;
import android.os.SystemClock;
import org.json.JSONObject;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class LocalHttpServer {
    private final Context context;
    private final KaiDb db;
    private final ExecutorService pool = Executors.newCachedThreadPool();
    private volatile boolean running;
    private ServerSocket serverSocket;
    private final long startedAt = SystemClock.elapsedRealtime();

    public LocalHttpServer(Context context) {
        this.context = context.getApplicationContext();
        this.db = new KaiDb(this.context);
    }

    public synchronized void start() throws IOException {
        if (running) return;
        serverSocket = new ServerSocket();
        serverSocket.setReuseAddress(true);
        serverSocket.bind(new InetSocketAddress(InetAddress.getByName("127.0.0.1"), 8000));
        running = true;
        db.event("backend_start", "{\"port\":8000}");
        pool.execute(this::acceptLoop);
    }

    public synchronized void stop() {
        running = false;
        try { if (serverSocket != null) serverSocket.close(); } catch (IOException ignored) {}
        pool.shutdownNow();
        db.event("backend_stop", "{}");
    }

    private void acceptLoop() {
        while (running) {
            try {
                Socket socket = serverSocket.accept();
                pool.execute(() -> handle(socket));
            } catch (IOException e) {
                if (running) e.printStackTrace();
            }
        }
    }

    private void handle(Socket socket) {
        try (Socket s = socket;
             BufferedReader reader = new BufferedReader(new InputStreamReader(s.getInputStream(), StandardCharsets.UTF_8));
             OutputStream out = s.getOutputStream()) {

            s.setSoTimeout(4000);
            String requestLine = reader.readLine();
            if (requestLine == null || requestLine.trim().isEmpty()) return;

            String[] parts = requestLine.split(" ");
            if (parts.length < 2) {
                writeJson(out, 400, new JSONObject().put("ok", false).put("error", "bad request"));
                return;
            }

            String method = parts[0].toUpperCase(Locale.ROOT);
            String path = parts[1].split("\\?", 2)[0];
            int contentLength = 0;
            String line;
            while ((line = reader.readLine()) != null && !line.isEmpty()) {
                int idx = line.indexOf(':');
                if (idx > 0 && line.substring(0, idx).trim().equalsIgnoreCase("Content-Length")) {
                    try { contentLength = Integer.parseInt(line.substring(idx + 1).trim()); } catch (NumberFormatException ignored) {}
                }
            }

            if (contentLength > 1024 * 1024) {
                writeJson(out, 413, new JSONObject().put("ok", false).put("error", "body too large"));
                return;
            }

            String body = "";
            if (contentLength > 0) {
                char[] chars = new char[contentLength];
                int read = 0;
                while (read < contentLength) {
                    int n = reader.read(chars, read, contentLength - read);
                    if (n < 0) break;
                    read += n;
                }
                body = new String(chars, 0, read);
            }

            route(out, method, path, body);
        } catch (Exception ignored) {
        }
    }

    private void route(OutputStream out, String method, String path, String body) throws Exception {
        if ("GET".equals(method) && ("/".equals(path) || "/health".equals(path) || "/api/health".equals(path) || "/api/status".equals(path))) {
            JSONObject j = new JSONObject()
                .put("ok", true)
                .put("service", "kai9000-secure")
                .put("host", "127.0.0.1")
                .put("port", 8000)
                .put("uptime_seconds", (SystemClock.elapsedRealtime() - startedAt) / 1000L)
                .put("package", context.getPackageName())
                .put("secure_folder_ready", true);
            writeJson(out, 200, j);
            return;
        }

        String prefix = "/api/kv/";
        if (path.startsWith(prefix) && path.length() > prefix.length()) {
            String key = URLDecoder.decode(path.substring(prefix.length()), StandardCharsets.UTF_8.name());
            if ("GET".equals(method)) {
                String value = db.get(key);
                if (value == null) {
                    writeJson(out, 404, new JSONObject().put("ok", false).put("error", "not found").put("key", key));
                } else {
                    Object parsed;
                    try { parsed = new JSONObject("{\"v\":" + value + "}").get("v"); }
                    catch (Exception e) { parsed = value; }
                    writeJson(out, 200, new JSONObject().put("ok", true).put("key", key).put("value", parsed));
                }
                return;
            }

            if ("POST".equals(method)) {
                JSONObject incoming = body.trim().isEmpty() ? new JSONObject() : new JSONObject(body);
                Object value = incoming.opt("value");
                String encoded = JSONObject.valueToString(value);
                db.put(key, encoded);
                db.event("kv_set", new JSONObject().put("key", key).toString());
                writeJson(out, 200, new JSONObject().put("ok", true).put("key", key).put("value", value));
                return;
            }
        }

        writeJson(out, 404, new JSONObject().put("ok", false).put("error", "not found"));
    }

    private static void writeJson(OutputStream out, int status, JSONObject body) throws IOException {
        byte[] bytes = body.toString().getBytes(StandardCharsets.UTF_8);
        String reason = status == 200 ? "OK" : status == 404 ? "Not Found" : status == 413 ? "Payload Too Large" : "Bad Request";
        String headers =
            "HTTP/1.1 " + status + " " + reason + "\r\n" +
            "Content-Type: application/json; charset=utf-8\r\n" +
            "Content-Length: " + bytes.length + "\r\n" +
            "Cache-Control: no-store\r\n" +
            "Connection: close\r\n" +
            "Access-Control-Allow-Origin: *\r\n\r\n";
        out.write(headers.getBytes(StandardCharsets.US_ASCII));
        out.write(bytes);
        out.flush();
    }
}
