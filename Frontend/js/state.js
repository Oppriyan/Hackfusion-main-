// MOCK DATABASES (temporary until backend connected)

export const MED_DB = [
  { name:'Paracetamol 500mg',stock:32,cat:'Pain Relief',reorder:10,price:2.06,restricted:false },
  { name:'Ibuprofen 200mg (Nurofen)',stock:5,cat:'Anti-inflammatory',reorder:15,price:10.98,restricted:false },
  { name:'Amoxicillin 500mg',stock:2,cat:'Antibiotic',reorder:20,price:8.50,restricted:true }
];

export let ordersDB = [
  { id:'#ORD576',cust:'PAT001 · F/45',med:'Panthenol Spray (1)',price:'€16.95',status:'Completed',payment:'Card' }
];

export let custsDB = [
  { id:'PAT001',name:'Anna M.',email:'pat001@pharmly.com',phone:'+49-151-0001',city:'Berlin',orders:6,status:'Active' }
];

export let invDB = [...MED_DB];

export const NOTIFS = [
  { icon:'⚠️',title:'Low Stock: Ibuprofen',time:'2 min ago' },
  { icon:'🔴',title:'Critical: Amoxicillin',time:'5 min ago' }
];

export let cartItems = [];