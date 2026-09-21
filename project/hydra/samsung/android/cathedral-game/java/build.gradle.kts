plugins {
    java
}

group = "art.eggiebagelface.luhm"
version = "0.1.0"

repositories {
    mavenCentral()
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}

dependencies {
    implementation("com.openai:openai-java:4.63.3")
    implementation("com.google.genai:google-genai:1.72.0")
    implementation("org.snakeyaml:snakeyaml-engine:2.10")
}

tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
    options.release.set(17)
}
