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
        versionCode = 9
        versionName = "0.9.0-dev"
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
    implementation("androidx.webkit:webkit:1.17.0")
}
