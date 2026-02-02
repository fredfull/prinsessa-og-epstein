# PDFer

Disse PDFene er skrapet fra https://www.justice.gov/epstein ved hjelp av å kjøre dette scriptet i utvikler-konsollen.
Query er søkeordet. Jeg har laget en mappe per søkeord her. Resultatene kommer i "page"s som inneholder 10 PDFer hver. I dette eksempelet stopper scriptet etter at maks fem pages er skrapet, det vil si maks femti pdfer.

```{javascript}
(async () => {
  const query = "kronprinsessen";
  let page = 0;
  let stop_after_pages = 5
  const delay = ms => new Promise(r => setTimeout(r, ms));

  let start_page = page;
  let seen = new Set();

  while (page <= start_page + stop_after_pages) {
    const url = `/multimedia-search?keys=${encodeURIComponent(query)}&page=${page}`;
    console.log("Fetching", url);

    const res = await fetch(url, { credentials: "include" });
    const data = await res.json();

    const hits = data?.hits?.hits || [];
    if (!hits.length) break;

    for (const hit of hits) {
      const pdf = hit?._source?.ORIGIN_FILE_URI;
      if (!pdf || seen.has(pdf)) continue;
      seen.add(pdf);

      const a = document.createElement("a");
      a.href = pdf;
      a.download = pdf.split("/").pop();
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      await delay(500); // be polite to the CDN
    }

    page++;
    await delay(1000);
  }

  console.log("Done. PDFs queued:", seen.size);
})();
```


