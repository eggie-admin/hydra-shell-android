package art.eggiebagelface.luhm;

import java.util.Map;
import java.util.Objects;

/** Provider-neutral authority boundary. This class performs no network or shell execution. */
public record AiPolicy(
        Provider provider,
        String apiKeyEnvironment,
        boolean advisoryOnly,
        boolean directShellExecution) {

    public enum Provider { OPENAI, GOOGLE }

    public AiPolicy {
        Objects.requireNonNull(provider, "provider");
        Objects.requireNonNull(apiKeyEnvironment, "apiKeyEnvironment");
        if (!advisoryOnly) {
            throw new IllegalArgumentException("LuHm AI providers must default to advisory-only");
        }
        if (directShellExecution) {
            throw new IllegalArgumentException("direct shell execution is forbidden");
        }
    }

    public String requireApiKey(Map<String, String> environment) {
        var value = environment.getOrDefault(apiKeyEnvironment, "").trim();
        if (value.isEmpty()) {
            throw new IllegalStateException("missing provider credential environment variable: " + apiKeyEnvironment);
        }
        return value;
    }

    public static AiPolicy openAi() {
        return new AiPolicy(Provider.OPENAI, "OPENAI_API_KEY", true, false);
    }

    public static AiPolicy google() {
        return new AiPolicy(Provider.GOOGLE, "GOOGLE_API_KEY", true, false);
    }
}
