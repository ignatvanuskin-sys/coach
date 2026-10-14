/* =========================================================
   Айгерим Серикова — лендинг бизнес-коуча
   Интерактив: меню, появление блоков, FAQ, заявка в WhatsApp
   ========================================================= */
(function () {
  'use strict';

  /* ---------- 1. Хедер при скролле ---------- */
  var head = document.getElementById('siteHead');
  var onScroll = function () {
    if (head) head.classList.toggle('is-scrolled', window.scrollY > 12);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---------- 2. Мобильное меню ---------- */
  var burger = document.getElementById('burger');
  var nav = document.getElementById('nav');

  function closeNav() {
    if (!nav || !burger) return;
    nav.classList.remove('is-open');
    burger.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('nav-open');
  }

  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.classList.toggle('nav-open', open);
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeNav();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeNav();
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 960) closeNav();
    });
  }

  /* ---------- 3. Появление блоков при скролле ---------- */
  var revealItems = document.querySelectorAll('.reveal');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealItems.forEach(function (el) { el.classList.add('is-visible'); });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    revealItems.forEach(function (el, i) {
      el.style.transitionDelay = (Math.min(i % 4, 3) * 70) + 'ms';
      observer.observe(el);
    });
  }

  /* ---------- 4. FAQ: одновременно открыт один вопрос ---------- */
  var faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(function (item) {
    item.addEventListener('toggle', function () {
      if (!item.open) return;
      faqItems.forEach(function (other) {
        if (other !== item) other.open = false;
      });
    });
  });

  /* ---------- 5. Кнопка тарифа → выбор в форме ---------- */
  var planSelect = document.getElementById('fPlan');
  document.querySelectorAll('[data-plan]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var value = btn.getAttribute('data-plan');
      if (!planSelect || !value) return;
      Array.prototype.forEach.call(planSelect.options, function (opt) {
        if (opt.text.trim().toLowerCase() === value.toLowerCase()) planSelect.value = opt.value || opt.text;
      });
    });
  });

  /* ---------- 6. Заявка → WhatsApp ---------- */
  var WHATSAPP_PHONE = '77771234567'; // ← замените на свой номер без «+»
  var form = document.getElementById('bookForm');
  var hint = document.getElementById('formHint');
  var defaultHint = hint ? hint.innerHTML : '';

  function buildMessage() {
    var name = (document.getElementById('fName').value || '').trim();
    var contact = (document.getElementById('fContact').value || '').trim();
    var plan = planSelect ? planSelect.value : '';
    var extra = (document.getElementById('fMessage').value || '').trim();

    var text = 'Здравствуйте, Айгерим! Меня зовут ' + name + '.';
    text += '\nФормат: ' + plan + '.';
    text += '\nКонтакт для связи: ' + contact + '.';
    if (extra) text += '\nПро ситуацию: ' + extra;
    text += '\nХочу записаться на консультацию.';
    return text;
  }

  function markError(field, isError) {
    if (!field) return;
    field.classList.toggle('is-error', isError);
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var nameField = document.getElementById('fName');
      var contactField = document.getElementById('fContact');
      var nameOk = nameField.value.trim().length >= 2;
      var contactOk = contactField.value.trim().length >= 5;

      markError(nameField, !nameOk);
      markError(contactField, !contactOk);

      if (!nameOk || !contactOk) {
        if (hint) {
          hint.textContent = 'Заполни, пожалуйста, имя и контакт для связи — иначе не смогу ответить.';
          hint.classList.remove('is-ok');
        }
        (nameOk ? contactField : nameField).focus();
        return;
      }

      var text = buildMessage();
      window.open('https://wa.me/' + WHATSAPP_PHONE + '?text=' + encodeURIComponent(text), '_blank', 'noopener');

      // текст заявки дублируем в буфер: если WhatsApp не открылся, его можно вставить в Telegram или письмо
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(function () {});
      }

      if (hint) {
        hint.innerHTML = 'Открываю WhatsApp с готовым текстом. Заявка также скопирована в буфер — её можно вставить в ' +
          '<a href="https://t.me/aigerim_coach" target="_blank" rel="noopener">Telegram</a> или письмо на hello@aigerim.coach.';
        hint.classList.add('is-ok');
      }
      form.reset();
    });

    // Telegram: копируем текст заявки в буфер, чтобы не набирать заново
    form.querySelectorAll('a[data-contact="telegram"]').forEach(function (link) {
      link.addEventListener('click', function () {
        var nameField = document.getElementById('fName');
        if (!nameField || nameField.value.trim().length < 2) return;
        var text = buildMessage();
        if (navigator.clipboard) navigator.clipboard.writeText(text).catch(function () {});
        if (hint) {
          hint.textContent = 'Текст заявки скопирован — просто вставь его в чат Telegram.';
          hint.classList.add('is-ok');
        }
      });
    });

    form.addEventListener('input', function (e) {
      if (e.target.matches('input,textarea')) markError(e.target, false);
      if (hint && hint.classList.contains('is-ok')) {
        hint.classList.remove('is-ok');
        hint.innerHTML = defaultHint;
      }
    });
  }

  /* ---------- 7. Плавающая кнопка WhatsApp ---------- */
  var waFloat = document.querySelector('.wa-float');
  var bookSection = document.getElementById('book');

  // показываем только после первого экрана — чтобы не перекрывать фото и заголовок
  if (waFloat) {
    var toggleFloat = function () {
      waFloat.classList.toggle('is-ready', window.scrollY > window.innerHeight * 0.75);
    };
    toggleFloat();
    window.addEventListener('scroll', toggleFloat, { passive: true });
  }

  if (waFloat && bookSection && 'IntersectionObserver' in window) {
    var bookObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        waFloat.classList.toggle('is-hidden', entry.isIntersecting);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -18% 0px' });
    bookObserver.observe(bookSection);
  }

  /* ---------- 8. Год в подвале ---------- */
  var yearHolder = document.querySelector('[data-year]');
  if (yearHolder) yearHolder.textContent = new Date().getFullYear();
})();
