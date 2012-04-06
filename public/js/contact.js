(function () {
  'use strict';

  var ender = require('ender');

  ender.domReady(function () {
    ender('.contact button').bind('click', function () {
      var elem = ender(this);

      ender.ajax({
        'url': location.pathname + '?id=' + elem.parents('.contact').data('id'),
        'method': 'delete',
        'type': 'text',
        'success': function () {
          elem.parents('.contact').remove();
        },
        'error': function (err) {
          console.error('Error deleting id:', err);
        }
      });
    });

    ender('#show-add-contact-form').bind('click', function () {
      ender(this).addClass('hidden');
      ender('.add-contact-form').removeClass('hidden');
    });
  });
}());
