// Generated by CoffeeScript 1.6.3
(function() {
  $(function() {
    var $navbar, VERTICAL_BUFFER, checkAndLoadImages, isElementInViewport;
    $navbar = $('nav');
    $('#header-menu-icon').click(function() {
      return $navbar.toggleClass('active');
    });
    $('.message .icon-cancel').click(function() {
      var self;
      self = $(this).parent();
      return self.slideUp(200, function() {
        self.remove();
        if (!$('#message-list li').length) {
          return $('#message-list').remove();
        }
      });
    });
    if ($('.lazy-image').length) {
      VERTICAL_BUFFER = 500;
      isElementInViewport = function(el) {
        var rect;
        rect = el.getBoundingClientRect();
        return rect.top >= 0 - VERTICAL_BUFFER && rect.right <= $(window).width() && rect.bottom <= $(window).height() + VERTICAL_BUFFER && rect.left >= 0;
      };
      checkAndLoadImages = function() {
        return $('.lazy-image').each(function() {
          var src;
          if (isElementInViewport(this)) {
            if (window.devicePixelRatio > 1 && $(this).attr('data-src-retina')) {
              src = $(this).attr('data-src-retina');
            } else {
              src = $(this).attr('data-src');
            }
            $(this).attr('src', src);
            return $(this).removeClass('lazy-image');
          }
        });
      };
      return $(window).on('load scroll resize', checkAndLoadImages);
    }
  });

  $(function() {
    var MangaModelView, changePage, data, getPageNum, mangaModelView, nextChapter, pageList, pageNumRegex, payload, prevChapter;
    if ($('#template-manga').length) {
      payload = $('#payload').text();
      payload = atob(payload);
      data = JSON.parse(payload);
      pageList = data.page_list;
      pageNumRegex = new RegExp("#/page/(\\d+)/");
      getPageNum = function() {
        var pageNum;
        pageNum = pageNumRegex.exec(window.location.hash);
        if (!pageNum) {
          return 1;
        }
        pageNum = parseInt(pageNum[1]);
        if (pageNum < 1) {
          return 1;
        }
        if (pageNum > data.length) {
          return data.length;
        }
        return pageNum;
      };
      nextChapter = $('#manga-chapter-jump option:selected').next().val();
      prevChapter = $('#manga-chapter-jump option:selected').prev().val();
      MangaModelView = function() {
        var self;
        self = this;
        self.prevNum = function() {
          if (self.pageNum() <= 1) {
            return 1;
          } else {
            return self.pageNum() - 1;
          }
        };
        self.nextNum = function() {
          if (self.pageNum() >= pageList.length) {
            return pageList.length;
          } else {
            return self.pageNum() + 1;
          }
        };
        self.pageNum = ko.observable(getPageNum());
        self.page = ko.computed(function() {
          return pageList[self.pageNum() - 1];
        });
        self.prevUrl = ko.computed(function() {
          if (prevChapter && self.prevNum() === self.pageNum()) {
            return "" + prevChapter + "#/page/100/";
          }
          return "#/page/" + (self.prevNum()) + "/";
        });
        self.nextUrl = ko.computed(function() {
          if (nextChapter && self.nextNum() === self.pageNum()) {
            return "" + nextChapter + "#/page/1/";
          }
          return "#/page/" + (self.nextNum()) + "/";
        });
        self.jumpPage = function() {
          var targetPage;
          targetPage = $("#manga-page-jump").val();
          return window.location.hash = "#/page/" + targetPage + "/";
        };
        self.preload = function() {
          var preloadPage;
          preloadPage = function(page) {
            if (!page.loaded) {
              (new Image()).src = page.url;
              return page.loaded = true;
            }
          };
          preloadPage(pageList[self.prevNum() - 1]);
          return preloadPage(pageList[self.nextNum() - 1]);
        };
        self.double = function() {
          return self.page().double;
        };
        self.preload();
      };
      mangaModelView = new MangaModelView();
      ko.applyBindings(mangaModelView);
      changePage = function() {
        var pageNum, scrollTop;
        pageNum = getPageNum();
        mangaModelView.pageNum(pageNum);
        mangaModelView.preload();
        if (pageNum === 1) {
          scrollTop = 0;
        } else {
          scrollTop = $('.manga-main').offset().top - 10;
        }
        $('html, body').animate({
          scrollTop: scrollTop
        }, 100);
      };
      $(window).bind('hashchange', changePage);
      $(document).keydown(function(e) {
        if ($('textarea').is(':focus')) {
          return;
        }
        if (e.which === 37) {
          window.location = mangaModelView.prevUrl();
        }
        if (e.which === 39) {
          window.location = mangaModelView.nextUrl();
        }
      });
    }
  });

  $(function() {
    if ($('#template-manga-info').length) {
      return $('h2').click(function() {
        var id;
        id = $(this).attr('id');
        return $("[data-section=" + id + "]").toggleClass('active');
      });
    }
  });

  $(function() {
    var autocompleteParams, bindAutocompleteKeydown, extractLast, split, success;
    if ($('#template-manga-edit').length) {
      split = function(val) {
        return val.split(/,\s*/);
      };
      extractLast = function(term) {
        return split(term).pop();
      };
      bindAutocompleteKeydown = function(e) {
        if (e.keyCode === $.ui.keyCode.TAB && $(this).data('ui-autocomplete').menu.active) {
          return e.preventDefault();
        }
      };
      autocompleteParams = function(source) {
        return {
          source: function(request, response) {
            var results;
            results = $.ui.autocomplete.filter(source, extractLast(request.term));
            return response(results.slice(0, 10));
          },
          delay: 0,
          focus: function() {
            return false;
          },
          select: function(e, ui) {
            var terms;
            terms = split(this.value);
            terms.pop();
            terms.push(ui.item.value);
            terms.push('');
            this.value = terms.join(', ');
            return false;
          }
        };
      };
      success = function(data) {
        $('#id_authors').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.AUTHOR));
        $('#id_circles').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.CIRCLE));
        $('#id_content').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.CONTENT));
        $('#id_events').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.EVENT));
        $('#id_magazines').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.MAGAZINE));
        $('#id_parodies').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.PARODY));
        $('#id_scanlators').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.SCANLATOR));
        $('#id_collection').bind('keydown', bindAutocompleteKeydown).autocomplete({
          source: data.COLLECTION,
          delay: 0
        });
        return $('#id_tank').bind('keydown', bindAutocompleteKeydown).autocomplete({
          source: data.TANK,
          delay: 0
        });
      };
      return $.get('/tag/autocomplete.json', success);
    }
  });

  $(function() {
    var $deleteButton, $imageList, $imageOrderInput, $setCoverButton, update_buttons;
    if ($('#template-manga-edit-images').length) {
      $('input[type="file"]').change(function() {
        return $(this).parents('form').submit();
      });
      $imageList = $('.mtl');
      if ($imageList.length) {
        $imageList.sortable();
        $imageOrderInput = $imageList.find('input[id$="ORDER"]');
        $imageOrderInput.attr('readonly', 'readonly');
        $imageOrderInput.attr('type', 'text');
        $imageList.bind('sortstop', function(event, ui) {
          var i, item, _i, _len, _ref, _results;
          _ref = $('.mtli');
          _results = [];
          for (i = _i = 0, _len = _ref.length; _i < _len; i = ++_i) {
            item = _ref[i];
            _results.push($(item).find('input[id$="ORDER"]').attr('value', i + 1));
          }
          return _results;
        });
      }
      $setCoverButton = $('#id_button_set_cover');
      $deleteButton = $('#id_button_delete');
      update_buttons = function() {
        var selected_count;
        selected_count = $('.mp-select:checked').length;
        if (selected_count === 1) {
          $setCoverButton.removeAttr('disabled');
        } else {
          $setCoverButton.attr('disabled', 'disabled');
        }
        if (selected_count > 0) {
          return $deleteButton.removeAttr('disabled');
        } else {
          return $deleteButton.attr('disabled', 'disabled');
        }
      };
      $('.mp-select').on('change', update_buttons);
      return update_buttons();
    }
  });

}).call(this);
