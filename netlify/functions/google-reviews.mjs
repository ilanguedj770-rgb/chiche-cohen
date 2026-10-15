// Avis Google de la fiche « Maître Ilan GUEDJ - Avocat dommage corporel ».
//
// Interroge l'API Places (New) côté serveur pour que la clé ne soit jamais
// exposée au navigateur, puis renvoie un JSON allégé à la page d'accueil.
// La réponse est mise en cache 24 h sur le CDN Netlify (cache « durable »,
// partagé entre les nœuds) : environ un appel à Google par jour, ce qui reste
// très en deçà du quota gratuit mensuel.
//
// Variables d'environnement (portée « Functions ») :
//   GOOGLE_PLACES_API_KEY  clé Google Maps Platform, API « Places API (New) » activée
//   GOOGLE_PLACE_ID        facultatif, remplace l'identifiant de fiche ci-dessous

const DEFAULT_PLACE_ID = "ChIJ7_fUSMPByRIR7Nq6quN5q9M";
const FIELDS = "rating,userRatingCount,googleMapsUri,reviews";

const json = (body, { status = 200, cdnMaxAge = 86400 } = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
      "Netlify-CDN-Cache-Control": `public, durable, s-maxage=${cdnMaxAge}, stale-while-revalidate=86400`,
      "X-Robots-Tag": "noindex",
    },
  });

export const toPayload = (place, placeId) => ({
  rating: typeof place.rating === "number" ? place.rating : null,
  count: typeof place.userRatingCount === "number" ? place.userRatingCount : 0,
  mapsUri: place.googleMapsUri || `https://www.google.com/maps/place/?q=place_id:${placeId}`,
  writeReviewUri: `https://search.google.com/local/writereview?placeid=${placeId}`,
  reviews: (place.reviews || [])
    .map((r) => {
      // On privilégie les mots du client ; la traduction de Google ne sert
      // que pour un avis rédigé dans une autre langue que le français.
      const original = r.originalText || {};
      const isFrench = (original.languageCode || "").toLowerCase().startsWith("fr");
      const text = ((isFrench ? original.text : r.text?.text) || original.text || "").trim();
      return {
        author: r.authorAttribution?.displayName || "Client Google",
        authorUri: r.authorAttribution?.uri || null,
        photo: r.authorAttribution?.photoUri || null,
        rating: r.rating || 0,
        when: r.relativePublishTimeDescription || "",
        publishTime: r.publishTime || null,
        text,
        translated: !isFrench && Boolean(r.text?.text),
        reviewUri: r.googleMapsUri || null,
      };
    })
    .filter((r) => r.text),
});

export default async () => {
  const apiKey = Netlify.env.get("GOOGLE_PLACES_API_KEY");
  const placeId = Netlify.env.get("GOOGLE_PLACE_ID") || DEFAULT_PLACE_ID;

  if (!apiKey) {
    return json({ error: "missing_api_key" }, { status: 503, cdnMaxAge: 300 });
  }

  try {
    const res = await fetch(
      `https://places.googleapis.com/v1/places/${encodeURIComponent(placeId)}?languageCode=fr&regionCode=FR`,
      { headers: { "X-Goog-Api-Key": apiKey, "X-Goog-FieldMask": FIELDS } },
    );
    if (!res.ok) {
      console.error("Places API", res.status, await res.text());
      return json({ error: "upstream_error" }, { status: 502, cdnMaxAge: 300 });
    }
    return json(toPayload(await res.json(), placeId));
  } catch (err) {
    console.error("Places API", err);
    return json({ error: "upstream_unreachable" }, { status: 502, cdnMaxAge: 300 });
  }
};

export const config = { path: "/api/avis-google", method: "GET" };
