var updateBtns = document.getElementsByClassName("update-cart");

for (i = 0; i < updateBtns.length; i++) {
  updateBtns[i].addEventListener("click", function () {
    var productId = this.dataset.product;
    var action = this.dataset.action;
    console.log("productId:", productId, "Action:", action);
    console.log("USEER:", user);

    if (user === "AnonymousUser") {
      addCookieItem(productId, action);
    } else {
      updateUserOrder(productId, action);
    }
  });
}

function getCookie(name) {
  var cookieArr = document.cookie.split(";");

  for (var i = 0; i < cookieArr.length; i++) {
    var cookiePair = cookieArr[i].split("=");

    if (name == cookiePair[0].trim()) {
      return decodeURIComponent(cookiePair[1]);
    }
  }
  return null;
}

var cart = JSON.parse(getCookie("cart")) || {}; // Fallback to an empty object

if (Object.keys(cart).length === 0) {
  // Check if cart is empty
  console.log("Cart Created!", cart);
  document.cookie =
    "cart=" + encodeURIComponent(JSON.stringify(cart)) + "; path=/";
}

console.log("Cart:", cart);

function addCookieItem(productId, action) {
  console.log("User is not authenticated");

  if (action == "add") {
    if (cart[productId] == undefined) {
      cart[productId] = { quantity: 1 };
    } else {
      cart[productId]["quantity"] += 1;
    }
  }

  if (action == "remove") {
    if (cart[productId]) {
      cart[productId]["quantity"] -= 1;

      if (cart[productId]["quantity"] <= 0) {
        console.log("Removed Item");
        delete cart[productId];
      }
    }
  }

  console.log("Updated Cart: ", cart);
  document.cookie =
    "cart=" + encodeURIComponent(JSON.stringify(cart)) + "; path=/";
  location.reload();
}

function updateUserOrder(productId, action) {
  console.log("User is logged in, sending data...");

  const url = "/update_item/";

  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ productId: productId, action: action }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      console.log("Success:", data);
      location.reload();
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
}
