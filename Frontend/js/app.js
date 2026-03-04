import {initNavigation} from "./modules/navigation.js";
import {initToast} from "./modules/toast.js";
import {initModals} from "./modules/modals.js";
import {initNotifications} from "./modules/notifications.js";
import {initShop} from "./modules/shop.js";
import {initCart} from "./modules/cart.js";
import {initSearch} from "./modules/search.js";
import {initChatbot} from "./modules/chatbot.js";
import {initDashboard} from "./modules/dashboard.js";
import {initAdmin} from "./modules/admin.js";
import {initPayment} from "./modules/payment.js";

document.addEventListener("DOMContentLoaded",()=>{

initNavigation();
initToast();
initModals();
initNotifications();
initShop();
initCart();
initSearch();
initChatbot();
initDashboard();
initAdmin();
initPayment();

});