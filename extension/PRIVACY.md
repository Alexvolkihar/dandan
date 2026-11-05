# Privacy policy: Dandan Furigana browser extension

Last updated: 2026-11-05

The Dandan Furigana extension collects no data and sends none anywhere.

- **No network requests.** The font, the stylesheet and the popup are all inside the extension. It never
  contacts a server, including the Dandan website (the link in the popup only opens it when you click it).
- **No analytics, no tracking, no ads.**
- **What it stores.** Your settings, in the browser's local extension storage on your device: whether the
  extension is on by default, the JLPT level, the scope, the line height, and the list of sites you turned on or
  off (as `https://example.com` origins). They are never synced or uploaded by the extension. Uninstalling the
  extension deletes them.
- **What it reads on a page.** On a site where you turned it on, the extension reads the text of the page in
  your browser to find Japanese text, and the fonts the page uses, so it can apply the Dandan font to that text.
  Nothing it reads leaves the page.

## Permissions

| Permission | Why |
| --- | --- |
| `storage` | Keep your settings on your device. |
| `activeTab` | Read the address of the current tab when you open the popup, to show and change its setting. |
| `scripting` | Run the script that marks Japanese text, and insert the font stylesheet, on the sites you turned on. |
| Access to a site (asked when you turn the extension on for it) | Apply the font on that site, now and on later visits. Turning the site off gives the access back. |
| Access to all sites (asked only if you choose "On for all sites") | Apply the font on every site except those you turned off. |

The extension does nothing on a site until you turn it on there. You can review or revoke site access at any
time in the browser's extension settings.

One side effect to know about: while access is granted, a web page can tell that the extension is installed by
trying to load its font file. The font is the only file pages can reach.

## Contact

Alexis MABANZA, via <https://dandan.alexvolkihar.ovh> or the project's issue tracker.
