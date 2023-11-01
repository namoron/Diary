jQuery(function () {
  var appear = false;
  var pagetop = $("#page_top");
  $(window).scroll(function () {
    if ($(this).scrollTop() > 100) {
      //100pxスクロールしたら
      if (appear == false) {
        appear = true;
        pagetop.stop().animate(
          {
            bottom: "50px", //下から50pxの位置に
          },
          300
        ); //0.3秒かけて現れる
      }
    } else {
      if (appear) {
        appear = false;
        pagetop.stop().animate(
          {
            bottom: "-50px", //下から-50pxの位置に
          },
          300
        ); //0.3秒かけて隠れる
      }
    }
  });
  pagetop.click(function () {
    $("body, html").animate({ scrollTop: 0 }, 500); //0.5秒かけてトップへ戻る
    return false;
  });
});

$(document).ready(function () {
  $("#formSelect").on("change", function () {
    var fileName = $(this).val().split("\\").pop(); // ファイル名を取得
    $("#fileName").text(fileName); // ファイル名を表示する要素にセット
    $("#fileName").show(); // ファイル名を表示

    // 画像の表示
    var fileInput = this;
    if (fileInput.files && fileInput.files[0]) {
      var reader = new FileReader();

      reader.onload = function (e) {
        $("#selectedImage").attr("src", e.target.result);
        $("#imageContainer").show();
      };

      reader.readAsDataURL(fileInput.files[0]);
    }
  });
});

$(document).ready(function () {
  $("#formSelect").on("change", function () {
    var fileName = $(this).val().split("\\").pop();
    $("#fileName").text(fileName);
    $("#fileName").show();

    var fileInput = this;
    if (fileInput.files && fileInput.files[0]) {
      var reader = new FileReader();

      reader.onload = function (e) {
        $("#selectedImage").attr("src", e.target.result);
        $("#imageContainer").show(); // 元の画像を非表示にする
        $("#editImage img").hide();
      };

      reader.readAsDataURL(fileInput.files[0]);
    }
  });
});
