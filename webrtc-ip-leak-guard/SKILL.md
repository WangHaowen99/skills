---
name: webrtc-ip-leak-guard
description: Diagnose and reduce Windows IP privacy leaks involving WebRTC, DNS, IPv6, proxy bypasses, WinHTTP, browser policies, TUN/VPN adapters, split routing, and exposed direct egress IPs. Use when a user asks to check, interpret, or fix IP leak reports, WebRTC leak warnings, DNS leak warnings, VPN/proxy consistency, or browser anti-leak policy on Windows.
---

# WebRTC IP Leak Guard

## Workflow

Use this skill to inspect and harden Windows systems where browser or app traffic should appear from a VPN/proxy egress rather than the machine's direct network.

1. Identify the active privacy model: full VPN/TUN, local HTTP/SOCKS proxy, split tunnel, or direct network.
2. Compare direct egress, system-proxy egress, DNS resolver egress, IPv6 state, default routes, and browser WebRTC policy.
3. Explain findings as "observed value", "risk", and "fix".
4. Apply only low-risk, explicit fixes unless the user asks for stronger controls.
5. Ask the user to refresh a browser leak-test page after browser policy changes, because WebRTC is most accurately verified in the browser.

## Quick Commands

Run a read-only Windows report:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows-leak-check.ps1
```

Apply Chrome and Edge WebRTC anti-leak policies, then print a report:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows-leak-check.ps1 -FixWebRtcPolicies
```

Use a known local proxy port:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows-leak-check.ps1 -ProxyUrl http://127.0.0.1:7890
```

Use `-Json` when another script or agent needs structured output.

## Interpretation Rules

- If forced direct egress differs from proxy egress, the system is likely only using a browser/system proxy. WebRTC, UDP, DNS, CLI tools, and apps that ignore proxy settings can leak direct IP.
- If forced direct egress and proxy egress both show proxy/VPN IPs, TUN/VPN routing is probably active.
- If DNS server is a physical-network resolver or DNS whoami shows an ISP/local-country egress that differs from the intended proxy region, flag DNS consistency risk.
- If public IPv6 is present and the VPN/proxy does not handle IPv6, flag IPv6 leak risk. Link-local IPv6 only is not a public leak.
- If `Get-NetRoute 0.0.0.0/0` shows both a physical gateway and a tunnel gateway, inspect metrics and live egress tests before claiming a leak.
- If `WinHTTP` is direct while system proxy is enabled, note that Windows services and some CLI tools may bypass the user proxy.
- If proxy bypass lists include target sites such as `*example.com`, those sites may bypass the local proxy. With TUN active they may still be captured, but the configuration is inconsistent.
- If browser WebRTC policy is missing, recommend `disable_non_proxied_udp` for Chrome/Edge.

## Safe Fixes

Use these fixes when they match the user's goal:

- Chrome policy: set `HKLM:\Software\Policies\Google\Chrome\WebRtcIPHandling` to `disable_non_proxied_udp`.
- Edge policy: set `HKLM:\Software\Policies\Microsoft\Edge\WebRtcLocalhostIpHandling` to `disable_non_proxied_udp`.
- Tell the user to fully restart the browser and verify in `chrome://policy` or `edge://policy`.
- Prefer enabling VPN/TUN mode, DNS-over-proxy, DNS leak protection, and kill switch inside the user's VPN/proxy client.
- Clear unnecessary proxy bypass rules if the user needs all sites to use the same path.

Treat these as stronger fixes that need explicit user intent:

- Enabling Windows Firewall outbound blocking or kill-switch rules.
- Disabling IPv6 globally or per adapter.
- Changing DNS server addresses on physical adapters.
- Terminating browser or VPN/proxy processes.

## Browser Policy Notes

Read `references/windows-browser-policies.md` when browser policy details, registry paths, or verification steps matter.

## Reporting Format

Keep the final report short and concrete:

- Current direct egress IP
- Current proxy/VPN egress IP
- Whether TUN/VPN adapter is active
- DNS resolver and DNS whoami result
- IPv6 public-route status
- WebRTC browser policy status
- Remaining risks and next verification step

Always distinguish "this is confirmed by local commands" from "this needs a browser leak-test page".
