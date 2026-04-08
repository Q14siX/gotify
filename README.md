[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration-41BDF5?style=flat&logo=home-assistant&logoColor=white)](https://www.home-assistant.io/)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5?style=flat&logo=hacs&logoColor=white)](https://hacs.xyz/)
[![Version](https://img.shields.io/github/v/release/Q14siX/gotify?style=flat&color=41BDF5&label=Version)](https://github.com/Q14siX/gotify/releases/latest)
[![Maintained](https://img.shields.io/badge/Maintained%3F-yes-41BDF5?style=flat)](https://github.com/Q14siX/gotify)
[![Stars](https://img.shields.io/github/stars/Q14siX/gotify?style=flat&logo=github&color=41BDF5&label=Stars)](https://github.com/Q14siX/gotify/stargazers)
[![Languages](https://img.shields.io/badge/Languages-DE%20%7C%20EN-41BDF5?style=flat&logo=translate&logoColor=white)](#deutsch--german)
[![License](https://img.shields.io/github/license/Q14siX/gotify?style=flat&color=41BDF5&label=License)](https://github.com/Q14siX/gotify/blob/main/LICENSE)
[![Downloads](https://img.shields.io/github/downloads/Q14siX/gotify/total?style=flat&color=41BDF5&label=Downloads)](https://github.com/Q14siX/gotify/releases/latest)
[![Issues](https://img.shields.io/github/issues/Q14siX/gotify?style=flat&color=41BDF5&label=Issues)](https://github.com/Q14siX/gotify/issues)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Q14siX&repository=gotify&category=integration)

---
# Gotify HACS Integration

## Deutsch / German

### Überblick

**Gotify for Home Assistant** ist eine benutzerdefinierte, HACS-fähige Home-Assistant-Integration, mit der Du einen oder mehrere Gotify-Server komfortabel per Config-Flow einrichten und anschließend für Senden, Empfangen, Zustandsüberwachung und Automatisierung nutzen kannst.

Die Integration ist **vollständig zweisprachig** aufgebaut und bringt sowohl deutschsprachige als auch englischsprachige Übersetzungen für Benutzeroberfläche, Services, Config-Flow, Options-Flow und Entitätsnamen mit.

### Passende Home Assistant App

Für Gotify steht zusätzlich eine passende **Home Assistant App** zur Verfügung.

Diese App stellt einen vollständig selbst gehosteten **Gotify Server** direkt in Home Assistant bereit. Sie startet den Server lokal in Home Assistant, speichert Daten dauerhaft im App-Datenverzeichnis und bindet die Weboberfläche sauber über **Ingress**, **Öffnen**-Button und **Seitenleiste** ein.

Damit lassen sich beide Projekte sehr sinnvoll kombinieren:

- Die **App** stellt den Gotify-Server in Home Assistant bereit.
- Die **HACS-Integration** verbindet Home Assistant mit einem oder mehreren Gotify-Servern.
- Dadurch kannst Du einen lokal in Home Assistant betriebenen Gotify-Server direkt für Benachrichtigungen, Sensoren, Events, Streaming und Automationen nutzen.

Die App ist besonders dann interessant, wenn Du Gotify komplett innerhalb Deiner Home-Assistant-Umgebung selbst hosten möchtest.

### Wichtiger technischer Hinweis

Der sichtbare Integrationsname in Home Assistant lautet **Gotify**.

Die interne Domain der Integration lautet absichtlich **`gotify_bridge`**. Dadurch werden Kollisionen mit anderen Namensverwendungen von `gotify` im Home-Assistant-Umfeld vermieden, während die Oberfläche für den Nutzer weiterhin sauber und eindeutig **Gotify** anzeigt.

### Funktionsumfang

Die Integration bietet unter anderem folgende Funktionen:

- **Config-Flow-Wizard** mit logisch aufgeteilten Einrichtungsseiten
- **Mehrere parallel eingerichtete Instanzen** eines oder mehrerer Gotify-Server
- **Nachrichtenversand** über Anwendungs-Token
- **Nachrichtenempfang** und **Live-Streaming** über Client-Token und WebSocket
- **Notify-Entity** zur Nutzung in Automationen und Skripten
- **Sensoren** für Serverstatus, Version, Benutzerinformationen, Zähler und letzte Nachricht
- **Binärsensor** für den Status der WebSocket-Verbindung
- **Event-Entity** für eingehende Gotify-Nachrichten
- **Home-Assistant-Eventbus-Event** `gotify_bridge_message_received`
- **Services** zum Senden, Löschen, Leeren und Aktualisieren
- **Gerätezuordnung pro Integrationseintrag**, sodass jede eingerichtete Instanz als eigenes Gerät erscheint
- **Blueprints** in deutscher und englischer Sprache
- **HACS-kompatible Repository-Struktur** inklusive Brand-Assets

### Installation

#### Installation über HACS

1. Öffne HACS.
2. Füge dieses Repository als benutzerdefiniertes Integrations-Repository hinzu.
3. Installiere die Integration.
4. Starte Home Assistant neu.
5. Füge anschließend die Integration **Gotify** unter **Einstellungen → Geräte & Dienste** hinzu.

Direkt-Link für HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Q14siX&repository=gotify&category=integration)

#### Manuelle Installation

Kopiere den Ordner:

`custom_components/gotify_bridge`

nach:

`/config/custom_components/gotify_bridge/`

Wenn bereits ältere Teststände installiert waren, lösche vorher konsequent mögliche Altordner:

- `/config/custom_components/gotify/`
- `/config/custom_components/gotify_bridge/`

Starte danach Home Assistant vollständig neu.

### Einrichtung in Home Assistant

Die Integration wird über einen mehrstufigen Wizard eingerichtet. Die Seiten sind logisch getrennt, damit zusammengehörige Angaben nicht unnötig vermischt werden.

#### 1. Serververbindung

Hier werden die Grunddaten des Servers abgefragt:

- Anzeigename des Eintrags
- Server-URL
- SSL-Zertifikatsprüfung

#### 2. Zugriff und Berechtigungen

Hier legst Du fest, wie der Eintrag verwendet werden soll:

- **Vollzugriff**: Senden und Empfangen
- **Nur senden**: Nur Benachrichtigungen von HA nach Gotify
- **Nur empfangen**: Nur Empfang, Verwaltung und Streaming

Zusätzlich werden hier die jeweils benötigten Tokens erfasst.

#### 3. Aktualisierung und Streaming

Hier definierst Du das Betriebsverhalten:

- Polling-Intervall
- WebSocket-Aktivierung

#### 4. Überwachte Anwendung

Optional kann eine bestimmte Gotify-Anwendung ausgewählt werden, deren Nachrichten überwacht, gezählt oder gesammelt gelöscht werden sollen.

### Token-Typen und deren Bedeutung

#### Anwendungs-Token

Ein **Application Token** wird benötigt, wenn Home Assistant aktiv Nachrichten an Gotify senden soll.

Typische Verwendung:

- Statusmeldungen
- Alarmierungen
- Informations- und Servicenachrichten
- Weiterleitung von Home-Assistant-Ereignissen an mobile Gotify-Clients

#### Client-Token

Ein **Client Token** wird benötigt, wenn Home Assistant Daten vom Gotify-Server lesen oder Live-Nachrichten empfangen soll.

Typische Verwendung:

- Benutzerinformationen abrufen
- Anwendungslisten abrufen
- Nachrichtenlisten lesen
- Nachrichten löschen
- WebSocket-Stream für eingehende Nachrichten verwenden

### Entitäten

Je nach Konfiguration und Berechtigungen stellt die Integration mehrere Entitäten bereit.

#### Typische Sensoren

- Server-Version
- Server-Commit
- Server-Zustand
- Datenbank-Zustand
- Aktueller Benutzer
- Anzahl Anwendungen
- Anzahl Clients
- Anzahl überwachter Nachrichten
- Anzahl empfangener Nachrichten
- Titel der letzten Nachricht
- Priorität der letzten Nachricht

#### Binärsensor

- WebSocket-Verbindung

#### Event-Entity

- Eingehende Nachricht

#### Notify-Entity

- Benachrichtigungen

### Services

Die Integration registriert folgende Services unter der Domain `gotify_bridge`:

- `gotify_bridge.send_message`
- `gotify_bridge.delete_message`
- `gotify_bridge.clear_messages`
- `gotify_bridge.refresh`

#### `gotify_bridge.send_message`

Dient zum Senden einer Gotify-Nachricht.

Unterstützte Felder:

- `entry_id`
- `message`
- `title`
- `priority`
- `markdown`
- `click_url`
- `big_image_url`
- `intent_url`
- `extras`

Beispiel:

```yaml
action: gotify_bridge.send_message
data:
  title: "Home Assistant"
  message: "Die Waschmaschine ist fertig."
  priority: 5
  markdown: false
```

#### `gotify_bridge.delete_message`

Löscht eine Nachricht anhand ihrer numerischen Gotify-ID.

```yaml
action: gotify_bridge.delete_message
data:
  entry_id: "DEINE_ENTRY_ID"
  message_id: 123
```

#### `gotify_bridge.clear_messages`

Löscht alle Nachrichten der konfigurierten überwachten Anwendung.

```yaml
action: gotify_bridge.clear_messages
data:
  entry_id: "DEINE_ENTRY_ID"
```

#### `gotify_bridge.refresh`

Aktualisiert alle Daten des gewählten Eintrags sofort.

```yaml
action: gotify_bridge.refresh
data:
  entry_id: "DEINE_ENTRY_ID"
```

### Eventbus-Event für eingehende Nachrichten

Bei eingehenden Nachrichten veröffentlicht die Integration zusätzlich das Event:

`gotify_bridge_message_received`

Typische Event-Daten:

- `entry_id`
- `title`
- `message`
- `priority`
- `id`
- `appid`
- `date`
- `extras`
- `raw`

Dadurch kannst Du sehr flexible Automationen auf Basis eingehender Gotify-Nachrichten bauen.

### Blueprints

Die Integration bringt drei sofort nutzbare Blueprint-Typen mit — jeweils in **Deutsch** und **Englisch**.

#### Deutsche Blueprints

#### Nachricht bei Auslösung senden

RAW:
`https://raw.githubusercontent.com/Q14siX/gotify/main/blueprints/automation/gotify_bridge/de/send_message_on_trigger.yaml`

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FQ14siX%2Fgotify%2Fmain%2Fblueprints%2Fautomation%2Fgotify_bridge%2Fde%2Fsend_message_on_trigger.yaml)

#### Auf eingehende Nachricht reagieren

RAW:
`https://raw.githubusercontent.com/Q14siX/gotify/main/blueprints/automation/gotify_bridge/de/react_to_incoming_message.yaml`

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FQ14siX%2Fgotify%2Fmain%2Fblueprints%2Fautomation%2Fgotify_bridge%2Fde%2Freact_to_incoming_message.yaml)

#### WebSocket-Verbindung überwachen

RAW:
`https://raw.githubusercontent.com/Q14siX/gotify/main/blueprints/automation/gotify_bridge/de/monitor_websocket_connection.yaml`

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FQ14siX%2Fgotify%2Fmain%2Fblueprints%2Fautomation%2Fgotify_bridge%2Fde%2Fmonitor_websocket_connection.yaml)


#### Ablageorte im Repository

- `blueprints/automation/gotify_bridge/de/send_message_on_trigger.yaml`
- `blueprints/automation/gotify_bridge/de/react_to_incoming_message.yaml`
- `blueprints/automation/gotify_bridge/de/monitor_websocket_connection.yaml`

### Beispielideen für Automationen

- Sende eine Gotify-Nachricht, wenn Waschmaschine oder Trockner fertig sind.
- Reagiere auf eingehende Gotify-Nachrichten mit bestimmten Prioritäten.
- Lasse bei WebSocket-Ausfall eine Eskalationsbenachrichtigung erzeugen.
- Leite kritische Home-Assistant-Ereignisse an Gotify weiter.
- Nutze Gotify als zentrale mobile Alarmierungsstrecke.

### Fehlerbehebung

#### Die Integration lässt sich nicht hinzufügen

- Prüfe, ob der Ordner korrekt unter `/config/custom_components/gotify_bridge/` liegt.
- Prüfe, ob alte Teststände vollständig gelöscht wurden.
- Starte Home Assistant nach jedem Austausch der Dateien vollständig neu.

#### Die Integration lässt sich einrichten, empfängt aber nichts

- Prüfe, ob ein **Client Token** hinterlegt ist.
- Prüfe, ob der WebSocket-Stream aktiviert ist.
- Prüfe, ob der Gotify-Server vom Home-Assistant-System aus erreichbar ist.

#### Senden funktioniert nicht

- Prüfe, ob ein **Application Token** vorhanden ist.
- Prüfe, ob der Modus **Vollzugriff** oder **Nur senden** gewählt wurde.
- Prüfe Server-URL und SSL-Einstellungen.

#### Mehrere Einträge sind vorhanden und Services schlagen fehl

Wenn mehrere Gotify-Einträge eingerichtet sind, muss bei Service-Aufrufen gezielt die gewünschte `entry_id` angegeben werden.

### Repository-Struktur

```text
custom_components/gotify_bridge/
├── __init__.py
├── api.py
├── binary_sensor.py
├── brand/
├── config_flow.py
├── const.py
├── coordinator.py
├── diagnostics.py
├── entity.py
├── event.py
├── manifest.json
├── notify.py
├── sensor.py
├── services.yaml
├── system_health.py
└── translations/

blueprints/automation/gotify_bridge/
├── de/
└── en/
```

### Hinweis zu Logos und Brand-Assets

Das Repository enthält Brand-Assets im Integrationsordner `custom_components/gotify_bridge/brand/`, damit Home Assistant und HACS die Grafiken möglichst konsistent verwenden können.

---

# Gotify HACS Integration

## English

### Overview

**Gotify for Home Assistant** is a custom, HACS-ready Home Assistant integration that lets you configure one or more Gotify servers through a config flow and then use them for message sending, incoming message handling, state monitoring, and automation workflows.

The integration is **fully bilingual** and ships with German and English translations for the user interface, services, config flow, options flow, and entity names.

### Matching Home Assistant app

A matching **Home Assistant app** for Gotify is also available.

This app provides a fully self-hosted **Gotify Server** directly inside Home Assistant. It starts the server locally in Home Assistant, stores data persistently inside the app data directory, and cleanly integrates the web interface through **ingress**, the **Open** button, and the **sidebar**.

This makes both projects a very useful combination:

- The **app** provides the Gotify server inside Home Assistant.
- The **HACS integration** connects Home Assistant to one or more Gotify servers.
- This allows you to use a locally hosted Gotify server inside Home Assistant directly for notifications, sensors, events, streaming, and automations.

The app is especially useful if you want to self-host Gotify completely inside your Home Assistant environment.

### Important technical note

The visible integration name in Home Assistant is **Gotify**.

The internal domain is intentionally **`gotify_bridge`**. This avoids naming collisions with other `gotify` usages inside the Home Assistant ecosystem while still presenting a clean and user-friendly **Gotify** name in the UI.

### Feature set

The integration includes, among other things:

- **Config flow wizard** with logically separated setup pages
- **Multiple parallel instances** of one or more Gotify servers
- **Message sending** through application tokens
- **Message receiving** and **live streaming** through client tokens and WebSocket
- **Notify entity** for use in automations and scripts
- **Sensors** for server state, version, user information, counters, and last message data
- **Binary sensor** for the WebSocket connection state
- **Event entity** for incoming Gotify messages
- **Home Assistant event bus event** `gotify_bridge_message_received`
- **Services** for sending, deleting, clearing, and refreshing
- **One device per config entry**, so every configured instance appears as its own device
- **Blueprints** in German and English
- **HACS-compatible repository structure** including brand assets

### Installation

#### Install through HACS

1. Open HACS.
2. Add this repository as a custom integration repository.
3. Install the integration.
4. Restart Home Assistant.
5. Add the **Gotify** integration under **Settings → Devices & Services**.

Direct HACS button:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Q14siX&repository=gotify&category=integration)

#### Manual installation

Copy:

`custom_components/gotify_bridge`

to:

`/config/custom_components/gotify_bridge/`

If older test builds were installed before, remove legacy folders first:

- `/config/custom_components/gotify/`
- `/config/custom_components/gotify_bridge/`

Then restart Home Assistant completely.

### Setup in Home Assistant

The integration uses a multi-step setup wizard so related settings stay grouped together and easier to understand.

#### 1. Server connection

This page contains the basic connection details:

- Entry display name
- Server URL
- SSL certificate verification

#### 2. Access and permissions

Here you define how the entry should be used:

- **Full access**: send and receive
- **Send only**: notifications from HA to Gotify only
- **Receive only**: receive, manage, and stream only

This step also collects the required token types.

#### 3. Update and streaming

This step controls runtime behavior:

- Polling interval
- WebSocket enable/disable

#### 4. Monitored application

Optionally, a specific Gotify application can be selected for message monitoring, counters, and bulk deletion.

### Token types and what they do

#### Application token

An **application token** is required when Home Assistant should actively send notifications to Gotify.

Typical use cases:

- status updates
- alerts
- information messages
- forwarding Home Assistant events to mobile Gotify clients

#### Client token

A **client token** is required when Home Assistant should read data from the Gotify server or receive live messages.

Typical use cases:

- reading user information
- retrieving application lists
- reading message lists
- deleting messages
- using the WebSocket stream for incoming messages

### Entities

Depending on the configuration and token permissions, the integration creates several entities.

#### Typical sensors

- Server version
- Server commit
- Server health
- Database health
- Current user
- Applications count
- Clients count
- Monitored messages count
- Received messages total
- Last message title
- Last message priority

#### Binary sensor

- WebSocket connection

#### Event entity

- Incoming message

#### Notify entity

- Notifications

### Services

The integration registers the following services under the `gotify_bridge` domain:

- `gotify_bridge.send_message`
- `gotify_bridge.delete_message`
- `gotify_bridge.clear_messages`
- `gotify_bridge.refresh`

#### `gotify_bridge.send_message`

Used to send a Gotify message.

Supported fields:

- `entry_id`
- `message`
- `title`
- `priority`
- `markdown`
- `click_url`
- `big_image_url`
- `intent_url`
- `extras`

Example:

```yaml
action: gotify_bridge.send_message
data:
  title: "Home Assistant"
  message: "The washing machine has finished."
  priority: 5
  markdown: false
```

#### `gotify_bridge.delete_message`

Deletes a message by its numeric Gotify ID.

```yaml
action: gotify_bridge.delete_message
data:
  entry_id: "YOUR_ENTRY_ID"
  message_id: 123
```

#### `gotify_bridge.clear_messages`

Deletes all messages belonging to the configured monitored application.

```yaml
action: gotify_bridge.clear_messages
data:
  entry_id: "YOUR_ENTRY_ID"
```

#### `gotify_bridge.refresh`

Refreshes all data of the selected entry immediately.

```yaml
action: gotify_bridge.refresh
data:
  entry_id: "YOUR_ENTRY_ID"
```

### Event bus event for incoming messages

Whenever a new message is received, the integration also publishes:

`gotify_bridge_message_received`

Typical event data:

- `entry_id`
- `title`
- `message`
- `priority`
- `id`
- `appid`
- `date`
- `extras`
- `raw`

This makes it possible to build flexible automations based on incoming Gotify traffic.

### Blueprints

The integration includes three ready-to-use blueprint types — each available in **German** and **English**.

#### English blueprints

#### Send message on trigger

RAW:
`https://raw.githubusercontent.com/Q14siX/gotify/main/blueprints/automation/gotify_bridge/en/send_message_on_trigger.yaml`

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FQ14siX%2Fgotify%2Fmain%2Fblueprints%2Fautomation%2Fgotify_bridge%2Fen%2Fsend_message_on_trigger.yaml)

#### React to incoming message

RAW:
`https://raw.githubusercontent.com/Q14siX/gotify/main/blueprints/automation/gotify_bridge/en/react_to_incoming_message.yaml`

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FQ14siX%2Fgotify%2Fmain%2Fblueprints%2Fautomation%2Fgotify_bridge%2Fen%2Freact_to_incoming_message.yaml)

#### Monitor WebSocket connection

RAW:
`https://raw.githubusercontent.com/Q14siX/gotify/main/blueprints/automation/gotify_bridge/en/monitor_websocket_connection.yaml`

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FQ14siX%2Fgotify%2Fmain%2Fblueprints%2Fautomation%2Fgotify_bridge%2Fen%2Fmonitor_websocket_connection.yaml)


#### Repository paths

- `blueprints/automation/gotify_bridge/en/send_message_on_trigger.yaml`
- `blueprints/automation/gotify_bridge/en/react_to_incoming_message.yaml`
- `blueprints/automation/gotify_bridge/en/monitor_websocket_connection.yaml`

### Automation ideas

- Send a Gotify message when the washer or dryer is finished.
- React to incoming Gotify messages above a certain priority.
- Raise an alert when the WebSocket stream is disconnected.
- Forward critical Home Assistant events to Gotify.
- Use Gotify as a central mobile alerting channel.

### Troubleshooting

#### The integration cannot be added

- Check whether the folder exists at `/config/custom_components/gotify_bridge/`.
- Make sure all older test builds were removed completely.
- Fully restart Home Assistant after replacing the files.

#### The integration can be configured but receives nothing

- Check whether a **client token** is configured.
- Check whether the WebSocket stream is enabled.
- Verify that the Gotify server is reachable from the Home Assistant system.

#### Sending does not work

- Check whether an **application token** is configured.
- Make sure the mode is **Full access** or **Send only**.
- Verify the server URL and SSL settings.

#### Multiple entries exist and service calls fail

If multiple Gotify entries are configured, service calls need the correct `entry_id` to target the intended entry.

### Repository structure

```text
custom_components/gotify_bridge/
├── __init__.py
├── api.py
├── binary_sensor.py
├── brand/
├── config_flow.py
├── const.py
├── coordinator.py
├── diagnostics.py
├── entity.py
├── event.py
├── manifest.json
├── notify.py
├── sensor.py
├── services.yaml
├── system_health.py
└── translations/

blueprints/automation/gotify_bridge/
├── de/
└── en/
```

### Note about logos and brand assets

The repository contains brand assets in `custom_components/gotify_bridge/brand/` so that Home Assistant and HACS can consume the graphics as consistently as possible.
