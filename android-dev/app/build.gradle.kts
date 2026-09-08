plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "art.eggiebagelface.kai9000.devhost"
    compileSdk = 36

    defaultConfig {
        applicationId = "art.eggiebagelface.kai9000.devhost"
        minSdk = 29
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0-native-dev"
    }

    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}
