// Trip pages: full screen photo viewer (PhotoSwipe) showing each photo's caption.
import PhotoSwipeLightbox from "https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/photoswipe-lightbox.esm.min.js";
import PhotoSwipeDynamicCaption from "https://cdn.jsdelivr.net/npm/photoswipe-dynamic-caption-plugin@1.2.7/photoswipe-dynamic-caption-plugin.esm.js";

const lightbox = new PhotoSwipeLightbox({
  gallery: "#trip-gallery",
  children: ".trip-photo a",
  pswpModule: () => import("https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/photoswipe.esm.min.js"),
  bgOpacity: 0.97,
  showHideAnimationType: "zoom",
  imageClickAction: "close",
  tapAction: "close",
});

new PhotoSwipeDynamicCaption(lightbox, {
  type: "auto",
  captionContent: (slide) => slide.data.element.closest("figure").querySelector("figcaption").innerHTML,
});

lightbox.init();
