var $form, $dialog, $map, user_msg, user_place, site_url;
$form = $('#form');
$dialog = $('#dialog');
$map = $('#map');
site_url_ref = window.location.protocol + "//" + window.location.host;
site_url = new URL(site_url_ref);

var map;
var service;
var infowindow;
var zoom_lvl = 13;

var userDlg = "<tr class='d-flex'><td class='col-3 user_dlg'>Vous :</td><td class='col-9 user_dlg'>"
var grandPyDlg = "<tr class='d-flex'><td class='col-3'>GrandPy :</td><td class='col-9 new_dlg'>"
var eol = '</td></tr>'

function displayDlg(message) {
    // Display messages from Grandpy and highlights the latest one
    $('#dialog td').removeClass("new_dlg")
    $dialog.append(grandPyDlg + message + eol);
}

function displayWiki(title, content) {
    // Format and display information retrieved from Wikipedia API 
    var $wiki = $('#wiki');
    $('#wiki *').remove();
    var titleElt = document.createElement("h2");
    var contentElt = document.createElement("p");
    var moreElt = document.createElement("a");

    titleElt.textContent = title;
    contentElt.innerHTML = content;
    moreElt.textContent = "En savoir plus";
    moreElt.href = "https://fr.wikipedia.org/wiki/" + title.replace(/ /g, "_");
    $wiki.append(titleElt, contentElt, moreElt);

    displayDlg("Cela me fait penser à une histoire... je te raconte, regarde un peu plus bas")
}


function displayMap(answers) {
    // From AJAX received info, displays Google Maps block
    if (answers["map_status"] === "KO") {
        displayDlg("Oh, mais tu es un filou ! Tu ne m'as pas demandé une adresse !")
    }
    else {
        // Build Map éléments - code part provided by google API
        var city = new google.maps.LatLng(47.070503, 2.253965);

        infowindow = new google.maps.InfoWindow();

        map = new google.maps.Map(
            document.getElementById('map'), {center: city, zoom: zoom_lvl});

        user_place = answers["coord"]
        createMarker(user_place);
        map.setCenter(user_place.location);
        
        // Once map is built and diplayed, add a message from GrandPy and display wiki related info
        displayDlg(" Voici l'adresse : " + answers["address"] + "<br>Je te montre le plan juste en dessous !");
        
        displayWiki(answers["wiki_page_title"], answers["wiki_snippet"]);

    }
    // Once AJAX request's callback is done, reset user's input field and stop displaying waiting image
    $('input:text').val('');
    $form.loadingView({'state':false});
}

function createMarker(place) {
    // Maps details such as place's marker - display function provided by Google API
    var marker = new google.maps.Marker({
        map: map,
        position: place.location
    });

    google.maps.event.addListener(marker, 'click', function() {
        infowindow.setContent(place.name);
        infowindow.open(map, this);
    });
}

$form.on('submit', function(event) {
    event.preventDefault();
    if ($('input:text').val() === "") {
        displayDlg("Petit coquin, tu ne m'as rien demandé !")
    }
    else {
        // Display image showing server's looking for requested info
        $form.loadingView({
            'image':"static/img/loadingImage.gif",
            'state':true
        });
        user_msg = $('input:text').val();

        // AJAX request through fake url - display retreived information launched as callback
        $.getJSON({
            url: site_url.href + '_question',
            data: {msg: user_msg},
            success: displayMap
        });

        $dialog.append(userDlg + user_msg + eol)
        displayDlg("Bien sûr mon poussin ! Laisse-moi chercher...")
    }
});
