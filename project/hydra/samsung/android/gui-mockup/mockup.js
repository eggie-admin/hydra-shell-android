(() => {
  'use strict';

  const body = document.body;
  const modeReceipt = document.getElementById('modeReceipt');
  const realmReceipt = document.getElementById('realmReceipt');
  const realmReceiptSide = document.getElementById('realmReceiptSide');
  const tierReceipt = document.getElementById('tierReceipt');

  const activate = (selector, attribute, value) => {
    document.querySelectorAll(selector).forEach((button) => {
      button.classList.toggle('active', button.getAttribute(attribute) === value);
    });
  };

  document.querySelectorAll('[data-mode-target]').forEach((button) => {
    button.addEventListener('click', () => {
      const mode = button.dataset.modeTarget;
      body.dataset.mode = mode;
      modeReceipt.textContent = mode;
      activate('[data-mode-target]', 'data-mode-target', mode);
    });
  });

  document.querySelectorAll('[data-realm-target]').forEach((button) => {
    button.addEventListener('click', () => {
      const realm = button.dataset.realmTarget;
      body.dataset.realm = realm;
      realmReceipt.textContent = realm;
      realmReceiptSide.textContent = realm;
      activate('[data-realm-target]', 'data-realm-target', realm);
    });
  });

  document.querySelectorAll('[data-tier-target]').forEach((button) => {
    button.addEventListener('click', () => {
      const tier = button.dataset.tierTarget;
      body.dataset.tier = tier;
      tierReceipt.textContent = tier;
      activate('[data-tier-target]', 'data-tier-target', tier);
    });
  });
})();
