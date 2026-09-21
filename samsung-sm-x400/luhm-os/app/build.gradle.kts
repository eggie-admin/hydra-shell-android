plugins {
    id("com.android.application")
}

android {
    namespace = "art.eggiebagelface.kai9000.dev"
    compileSdk = 37
    enableKotlin = false

    defaultConfig {
        applicationId = "art.eggiebagelface.kai9000.dev"
        minSdk = 31
        targetSdk = 37
        versionCode = 10
        versionName = "0.10.0-dev"
        ndk {
            abiFilters += listOf("arm64-v8a")
        }
    }

    buildFeatures {
        buildConfig = false
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    packaging {
        resources.excludes += setOf("META-INF/AL2.0", "META-INF/LGPL2.1")
    }
}

dependencies {
    implementation("org.godotengine:godot:4.7.2.stable")
}
