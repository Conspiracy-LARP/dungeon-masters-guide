<?xml version="1.0" encoding="UTF-8"?>
<!--
  A browser-only stylesheet for sitemap.xml.

  A crawler never sees this: it reads the raw <urlset> and ignores the
  <?xml-stylesheet?> processing instruction that points here. A human who opens
  sitemap.xml in a browser gets this rendered table instead of a wall of XML.
  Original work; nothing here is derived from another project's stylesheet.

  XSLT 1.0 on purpose — it is the only version browsers apply client-side.
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:s="http://www.sitemaps.org/schemas/sitemap/0.9">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>

  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title>Sitemap — Conspiracy LARP</title>
        <style>
          :root { color-scheme: light dark;
            --fg:#1a1a1a; --bg:#faf9f7; --dim:#5f5f5f; --line:#e4e1db;
            --head:#932a2a; --row:#ffffff; --zebra:#f4f2ee; --link:#8a2a24; }
          @media (prefers-color-scheme: dark) {
            :root { --fg:#e8e6e2; --bg:#141414; --dim:#9a9a9a; --line:#2e2e2e;
              --head:#e8857c; --row:#1b1b1b; --zebra:#181818; --link:#e8857c; }
          }
          * { box-sizing:border-box; }
          body { margin:0; padding:6vh 5vw; background:var(--bg); color:var(--fg);
            font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
          main { max-width:56rem; margin:0 auto; }
          h1 { font-family:Georgia,serif; font-size:1.9rem; margin:0 0 .2em; }
          p.sub { color:var(--dim); margin:0 0 2em; }
          p.sub b { color:var(--fg); }
          table { width:100%; border-collapse:collapse; font-size:.94em; }
          th { text-align:left; padding:.5em .7em; border-bottom:2px solid var(--head);
            color:var(--head); font-size:.8em; letter-spacing:.06em; text-transform:uppercase; }
          td { padding:.55em .7em; border-bottom:1px solid var(--line);
            vertical-align:top; word-break:break-word; }
          tr:nth-child(even) td { background:var(--zebra); }
          td.n { color:var(--dim); font-variant-numeric:tabular-nums; width:2.5rem; }
          td.d { color:var(--dim); white-space:nowrap; width:8rem; }
          a { color:var(--link); text-decoration:none; }
          a:hover { text-decoration:underline; }
          footer { margin-top:2.5em; color:var(--dim); font-size:.85em;
            border-top:1px solid var(--line); padding-top:1.2em; }
        </style>
      </head>
      <body>
        <main>
          <h1>Sitemap</h1>
          <p class="sub">
            <b><xsl:value-of select="count(s:urlset/s:url)"/></b>
            pages published on this site. This page is for people; search engines
            read the same file as data.
          </p>
          <table>
            <tr>
              <th>#</th><th>URL</th><th>Last changed</th>
            </tr>
            <xsl:for-each select="s:urlset/s:url">
              <tr>
                <td class="n"><xsl:value-of select="position()"/></td>
                <td>
                  <a href="{s:loc}"><xsl:value-of select="s:loc"/></a>
                </td>
                <td class="d"><xsl:value-of select="s:lastmod"/></td>
              </tr>
            </xsl:for-each>
          </table>
          <footer>
            Out-of-world: this listing describes the guide's own website, which is a
            manual and explains itself. The game is elsewhere.
          </footer>
        </main>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
