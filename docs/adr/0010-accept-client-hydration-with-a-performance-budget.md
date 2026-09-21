# Accept client hydration with a performance budget

Prerendered pages will ship complete, readable HTML and will not require Worker execution for delivery, but they may load TanStack Start's React client runtime and hydrate in the browser. This trade-off supports the deliberate goal of learning TanStack Start and enables interactive MDX without adopting a second rendering framework. Post-specific code will remain route-scoped, heavy hydration will be deferred only when measurement justifies it, and ordinary content must remain readable when JavaScript is unavailable.
