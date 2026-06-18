# Windows Browser Policies

Use browser policy when the user wants WebRTC leak protection that survives browser restarts and profile changes.

## Chrome

Registry path:

```powershell
HKLM:\Software\Policies\Google\Chrome
```

Value:

```powershell
WebRtcIPHandling = disable_non_proxied_udp
```

Verification:

1. Fully restart Chrome.
2. Open `chrome://policy`.
3. Click `Reload policies`.
4. Confirm `WebRtcIPHandling` is present.
5. Refresh a WebRTC leak-test page.

## Edge

Registry path:

```powershell
HKLM:\Software\Policies\Microsoft\Edge
```

Value:

```powershell
WebRtcLocalhostIpHandling = disable_non_proxied_udp
```

Verification:

1. Fully restart Edge.
2. Open `edge://policy`.
3. Click `Reload policies`.
4. Confirm `WebRtcLocalhostIpHandling` is present.
5. Refresh a WebRTC leak-test page.

## Meaning

`disable_non_proxied_udp` prevents WebRTC from using non-proxied UDP routes. This reduces the common leak where normal HTTPS traffic uses a proxy but WebRTC exposes the direct network IP through STUN.

This policy does not replace full VPN/TUN routing. If the system only uses a local HTTP/SOCKS proxy, DNS, UDP, CLI tools, and apps that ignore proxy settings can still bypass the proxy.
