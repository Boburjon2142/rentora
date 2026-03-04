(() => {
  const modal = document.getElementById('property-modal');
  if (!modal) return;

  const titleEl = document.getElementById('modal-title');
  const typeEl = document.getElementById('modal-type');
  const locationEl = document.getElementById('modal-location');
  const districtEl = document.getElementById('modal-district');
  const priceEl = document.getElementById('modal-price');
  const metaEl = document.getElementById('modal-meta');
  const viewsEl = document.getElementById('modal-views');
  const descriptionEl = document.getElementById('modal-description');
  const detailLinkEl = document.getElementById('modal-detail-link');
  const galleryEl = document.getElementById('modal-gallery');

  const openModal = (card) => {
    const imagesRaw = card.dataset.images || '';
    const images = imagesRaw ? imagesRaw.split('|').filter(Boolean) : [];

    titleEl.textContent = card.dataset.title || '';
    typeEl.textContent = card.dataset.type || "E'lon";
    locationEl.textContent = `${card.dataset.city || ''} - ${card.dataset.address || ''}`;
    districtEl.textContent = card.dataset.district || '';
    districtEl.style.display = card.dataset.district ? 'block' : 'none';
    priceEl.textContent = card.dataset.price || '';
    metaEl.textContent = card.dataset.meta || '';
    viewsEl.textContent = `Ko'rishlar: ${card.dataset.views || 0}`;
    descriptionEl.textContent = card.dataset.description || '';
    detailLinkEl.href = card.dataset.detailUrl || card.getAttribute('href') || '#';

    galleryEl.innerHTML = '';
    if (images.length) {
      images.slice(0, 3).forEach((src, idx) => {
        const img = document.createElement('img');
        img.src = src;
        img.alt = `${card.dataset.title || 'Property'} image ${idx + 1}`;
        galleryEl.appendChild(img);
      });
    } else {
      const empty = document.createElement('div');
      empty.className = 'property-modal__empty';
      empty.textContent = 'Rasm mavjud emas';
      galleryEl.appendChild(empty);
    }

    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
  };

  const closeModal = () => {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
  };

  document.querySelectorAll('.js-property-card').forEach((card) => {
    card.addEventListener('click', (event) => {
      event.preventDefault();
      openModal(card);
    });
  });

  modal.querySelectorAll('[data-modal-close]').forEach((el) => {
    el.addEventListener('click', closeModal);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modal.classList.contains('is-open')) {
      closeModal();
    }
  });
})();
