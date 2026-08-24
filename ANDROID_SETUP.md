# Configuración de Android (permisos y compilación)

Las carpetas `android/` e `ios/` NO se incluyen a mano en este proyecto,
porque `flutter create` las genera automáticamente ya emparejadas con la
versión exacta de tu Flutter SDK/Gradle/Kotlin instalada (si se copian de
otra máquina con otra versión, suelen fallar al compilar).

## Paso 1 — Generar las carpetas nativas

Desde la carpeta `flutter_app/` (donde está `pubspec.yaml`), ejecuta:

```bash
flutter create .
```

Esto crea `android/`, `ios/`, `web/`, etc. **sin tocar** tu carpeta `lib/`
ni tu `pubspec.yaml` ya existentes.

## Paso 2 — Editar `android/app/src/main/AndroidManifest.xml`

Abre ese archivo y agrega los permisos dentro de `<manifest ...>`, antes de
`<application ...>`:

```xml
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>

<uses-feature android:name="android.hardware.camera" android:required="true"/>
<uses-feature android:name="android.hardware.camera.autofocus" android:required="false"/>
```

Y dentro de la etiqueta `<application ...>` agrega (si no existe ya):

```xml
android:label="Sistema Asistencia"
android:usesCleartextTraffic="false"
```

## Paso 3 — Editar `android/app/build.gradle` (o `build.gradle.kts`)

Verifica/ajusta estos valores dentro del bloque `android { defaultConfig { ... } }`:

```gradle
minSdkVersion 21        // mobile_scanner y flutter_secure_storage lo requieren
targetSdkVersion 34
multiDexEnabled true
```

Si usas Kotlin DSL (`build.gradle.kts`), el equivalente es:

```kotlin
minSdk = 21
targetSdk = 34
multiDexEnabled = true
```

## Paso 4 — (Solo si vas a usar notificaciones locales)

En `android/app/src/main/AndroidManifest.xml`, dentro de `<application>`,
agrega el receiver que exige `flutter_local_notifications`:

```xml
<receiver android:exported="false" android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationReceiver" />
```

## Paso 5 — Aceptar licencias del Android SDK

Ya lo hiciste, pero por si el aviso persiste en `flutter doctor`:

```bash
flutter doctor --android-licenses
```

Acepta todas escribiendo `y` cuando se te pida.

## Paso 6 — Ejecutar

Con el emulador Pixel 7 (API 34+) corriendo, o un teléfono real conectado
por USB con depuración habilitada:

```bash
flutter pub get
flutter run
```

## Paso 7 — Generar el APK

```bash
flutter build apk --release
```

El archivo queda en:

```
flutter_app/build/app/outputs/flutter-apk/app-release.apk
```

Cópialo al teléfono e instálalo (puede requerir permitir "orígenes
desconocidos" en Android).
