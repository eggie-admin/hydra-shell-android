package art.eggiebagelface.kai9000secure;

import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;

import java.math.BigInteger;
import java.security.KeyPairGenerator;
import java.security.KeyStore;
import java.security.MessageDigest;
import java.security.PrivateKey;
import java.security.SecureRandom;
import java.security.cert.Certificate;
import java.security.cert.X509Certificate;
import java.util.Date;

import javax.net.ssl.KeyManager;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLServerSocket;
import javax.net.ssl.SSLServerSocketFactory;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509KeyManager;
import javax.net.ssl.X509TrustManager;
import javax.security.auth.x500.X500Principal;

public final class LocalTls {
    private static final String KEYSTORE = "AndroidKeyStore";
    private static final String ALIAS = "kai9000_local_tls_v1";
    private static final Object LOCK = new Object();

    private LocalTls() {}

    private static KeyStore keyStore() throws Exception {
        KeyStore ks = KeyStore.getInstance(KEYSTORE);
        ks.load(null);
        return ks;
    }

    private static void ensureIdentity() throws Exception {
        synchronized (LOCK) {
            KeyStore ks = keyStore();
            if (ks.containsAlias(ALIAS)) return;

            long now = System.currentTimeMillis();
            Date notBefore = new Date(now - 24L * 60L * 60L * 1000L);
            Date notAfter = new Date(now + 10L * 365L * 24L * 60L * 60L * 1000L);
            BigInteger serial = new BigInteger(64, new SecureRandom()).abs().add(BigInteger.ONE);

            KeyPairGenerator generator = KeyPairGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_RSA, KEYSTORE);
            KeyGenParameterSpec spec = new KeyGenParameterSpec.Builder(
                ALIAS,
                KeyProperties.PURPOSE_SIGN | KeyProperties.PURPOSE_VERIFY)
                .setKeySize(2048)
                .setDigests(KeyProperties.DIGEST_SHA256, KeyProperties.DIGEST_SHA512)
                .setSignaturePaddings(KeyProperties.SIGNATURE_PADDING_RSA_PKCS1)
                .setCertificateSubject(new X500Principal("CN=KAI9000 Secure Localhost"))
                .setCertificateSerialNumber(serial)
                .setCertificateNotBefore(notBefore)
                .setCertificateNotAfter(notAfter)
                .build();
            generator.initialize(spec);
            generator.generateKeyPair();
        }
    }

    public static X509Certificate certificate() throws Exception {
        ensureIdentity();
        Certificate cert = keyStore().getCertificate(ALIAS);
        if (!(cert instanceof X509Certificate)) {
            throw new IllegalStateException("TLS certificate unavailable");
        }
        return (X509Certificate) cert;
    }

    public static String fingerprintSha256() throws Exception {
        byte[] digest = MessageDigest.getInstance("SHA-256").digest(certificate().getEncoded());
        StringBuilder out = new StringBuilder(digest.length * 2);
        for (byte b : digest) out.append(String.format("%02x", b & 0xff));
        return out.toString();
    }

    public static SSLServerSocket newServerSocket() throws Exception {
        ensureIdentity();
        final KeyStore ks = keyStore();
        final PrivateKey privateKey = (PrivateKey) ks.getKey(ALIAS, null);
        final X509Certificate[] chain = certificateChain(ks);

        X509KeyManager keyManager = new X509KeyManager() {
            @Override public String[] getClientAliases(String keyType, java.security.Principal[] issuers) { return null; }
            @Override public String chooseClientAlias(String[] keyType, java.security.Principal[] issuers, java.net.Socket socket) { return null; }
            @Override public String[] getServerAliases(String keyType, java.security.Principal[] issuers) {
                return keyType != null && keyType.toUpperCase().contains("RSA") ? new String[]{ALIAS} : null;
            }
            @Override public String chooseServerAlias(String keyType, java.security.Principal[] issuers, java.net.Socket socket) {
                return keyType != null && keyType.toUpperCase().contains("RSA") ? ALIAS : null;
            }
            @Override public X509Certificate[] getCertificateChain(String alias) { return ALIAS.equals(alias) ? chain : null; }
            @Override public PrivateKey getPrivateKey(String alias) { return ALIAS.equals(alias) ? privateKey : null; }
        };

        SSLContext context = SSLContext.getInstance("TLS");
        context.init(new KeyManager[]{keyManager}, null, new SecureRandom());
        SSLServerSocketFactory factory = context.getServerSocketFactory();
        SSLServerSocket socket = (SSLServerSocket) factory.createServerSocket(
            8443, 50, java.net.InetAddress.getByName("127.0.0.1"));
        socket.setNeedClientAuth(false);
        return socket;
    }

    public static SSLSocketFactory pinnedClientSocketFactory() throws Exception {
        final byte[] expected = certificate().getEncoded();
        X509TrustManager trust = new X509TrustManager() {
            @Override public void checkClientTrusted(X509Certificate[] chain, String authType) throws java.security.cert.CertificateException {
                throw new java.security.cert.CertificateException("client certificates not accepted");
            }

            @Override public void checkServerTrusted(X509Certificate[] chain, String authType) throws java.security.cert.CertificateException {
                if (chain == null || chain.length == 0) throw new java.security.cert.CertificateException("missing server certificate");
                try {
                    byte[] actual = chain[0].getEncoded();
                    if (!MessageDigest.isEqual(expected, actual)) {
                        throw new java.security.cert.CertificateException("KAI9000 localhost certificate pin mismatch");
                    }
                } catch (java.security.cert.CertificateEncodingException e) {
                    throw new java.security.cert.CertificateException(e);
                }
            }

            @Override public X509Certificate[] getAcceptedIssuers() {
                try { return new X509Certificate[]{certificate()}; }
                catch (Exception e) { return new X509Certificate[0]; }
            }
        };

        SSLContext context = SSLContext.getInstance("TLS");
        context.init(null, new TrustManager[]{trust}, new SecureRandom());
        return context.getSocketFactory();
    }

    private static X509Certificate[] certificateChain(KeyStore ks) throws Exception {
        Certificate[] raw = ks.getCertificateChain(ALIAS);
        if (raw == null || raw.length == 0) return new X509Certificate[]{certificate()};
        X509Certificate[] out = new X509Certificate[raw.length];
        for (int i = 0; i < raw.length; i++) out[i] = (X509Certificate) raw[i];
        return out;
    }
}
