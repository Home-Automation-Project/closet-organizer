import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export default api

/**
 * DATA SOURCES
 * 
 * This application has been refactored to use:
 * - Static JSON files for: closets, family, first aid kits, cleaning schedules
 * - Google Sheets for: inventory items, reminders (via backend proxy)
 * - No database or MQTT dependencies
 */

// ---------------------------------------------------------------------------
// Closets (Static JSON)
// ---------------------------------------------------------------------------
export const getClosets = () => api.get('/closets')
export const getCloset = (id) => api.get(`/closets/${id}`)
export const createCloset = (data) => api.post('/closets', data)
export const updateCloset = (id, data) => api.put(`/closets/${id}`, data)
export const deleteCloset = (id) => api.delete(`/closets/${id}`)

// Shelves (Static JSON)
export const getShelves = (closetId) => api.get('/shelves', { params: { closet_id: closetId } })
export const createShelf = (data) => api.post('/shelves', data)
export const updateShelf = (id, data) => api.put(`/shelves/${id}`, data)
export const deleteShelf = (id) => api.delete(`/shelves/${id}`)

// Baskets (Static JSON)
export const getBaskets = (shelfId) => api.get('/baskets', { params: { shelf_id: shelfId } })
export const createBasket = (data) => api.post('/baskets', data)
export const updateBasket = (id, data) => api.put(`/baskets/${id}`, data)
export const deleteBasket = (id) => api.delete(`/baskets/${id}`)

// ---------------------------------------------------------------------------
// Inventory (Google Sheets via backend)
// ---------------------------------------------------------------------------
export const getBasketInventory = (basketId) => api.get(`/inventory/basket/${basketId}`)
export const upsertInventoryItem = (basketId, itemName, data) =>
  api.put(`/inventory/basket/${basketId}/item/${itemName}`, data)
export const deleteInventoryItem = (id) => api.delete(`/inventory/item/${id}`)
export const scanBasket = (qrToken) => api.get(`/inventory/scan/${qrToken}`)
export const getBasketQrUrl = (basketId) => `/api/inventory/basket/${basketId}/qr.png`

// ---------------------------------------------------------------------------
// Reminders (Google Sheets via backend)
// ---------------------------------------------------------------------------
export const getWashReminders = () => api.get('/reminders/wash')
export const acknowledgeWashReminder = (id) => api.patch(`/reminders/wash/${id}/acknowledge`)
export const getSeasonalReminders = () => api.get('/reminders/seasonal')
export const acknowledgeSeasonalReminder = (id) => api.patch(`/reminders/seasonal/${id}/acknowledge`)

// ---------------------------------------------------------------------------
// Cleaning (Static JSON)
// ---------------------------------------------------------------------------
export const getRooms = () => api.get('/cleaning/rooms')
export const getRoomChecklist = (room, sessionToken) =>
  api.get(`/cleaning/${room}`, { params: sessionToken ? { session_token: sessionToken } : {} })
export const completeItem = (room, itemKey, sessionToken) =>
  api.post(`/cleaning/${room}/complete/${itemKey}`, null, { params: { session_token: sessionToken } })
export const uncompleteItem = (room, itemKey, sessionToken) =>
  api.delete(`/cleaning/${room}/complete/${itemKey}`, { params: { session_token: sessionToken } })
export const resetSession = (room, sessionToken) =>
  api.delete(`/cleaning/${room}/session`, { params: { session_token: sessionToken } })

// ---------------------------------------------------------------------------
// First Aid (Static JSON)
// ---------------------------------------------------------------------------
export const getBasicKit = (category) =>
  api.get('/firstaid/kit/basic', { params: category ? { category } : {} })
export const getAdvancedBins = () => api.get('/firstaid/kit/advanced/bins')
export const getAdvancedKit = (subBin) =>
  api.get('/firstaid/kit/advanced', { params: subBin ? { sub_bin: subBin } : {} })
export const getCprSteps = () => api.get('/firstaid/cpr')

// ---------------------------------------------------------------------------
// Family (Static JSON)
// ---------------------------------------------------------------------------
export const getFamilyMembers = () => api.get('/family')
export const createFamilyMember = (data) => api.post('/family', data)
export const updateFamilyMember = (id, data) => api.put(`/family/${id}`, data)
export const deleteFamilyMember = (id) => api.delete(`/family/${id}`)
