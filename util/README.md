# Panel Command library (Java)

## Overview

This library is a command signer for Java.

To send command remotely is necessary that this command must have signature and MFA (Multi factor Authentication)

This library provide HMAC SHA 256 signing tool to be installed in any Java application

### Concecpt

```sh
result = signer(Secret Key, MFA, panel command)
```

See tests (TODO implement test)

## Install

```sh
mvn -U clean install
```

## Maven

```xml
    <dependencies>
        <dependency>
            <groupId>org.panelcommand</groupId>
            <artifactId>PanelCommand</artifactId>
            <version>1.0-SNAPSHOT</version>
        </dependency>
        ...
    <dependencies>
```

## Usage

```java
    PanelCommand panelCommand = new PanelCommand("Your secret key");
    long totp = 123456;
    int command = 1;

    String result = panelCommand.signMessageJsonString(totp, command);
    ...
```
