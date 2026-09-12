import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "art.eggiebagelface.kai9000.dev"
    compileSdk = 36

    defaultConfig {
        applicationId = "art.eggiebagelface.kai9000.dev"
        minSdk = 31
        targetSdk = 36
        versionCode = 8
        versionName = "0.8.0-dev"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlin {
        compilerOptions { jvmTarget.set(JvmTarget.JVM_17) }
    }
}

dependencies {
    implementation("androidx.webkit:webkit:1.17.0")
}
