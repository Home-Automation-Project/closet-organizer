<template>
  <div>
    <RouterLink to="/firstaid" class="text-muted text-sm">← First Aid Hub</RouterLink>
    <div class="flex items-center justify-between mt-3 mb-4">
      <h1 class="page-title" style="margin-bottom:0">Family Medical Info</h1>
      <button class="btn-primary" @click="openModal()">+ Add Member</button>
    </div>

    <div v-if="!members.length" class="card text-muted" style="text-align:center;padding:2rem">
      No family members added yet.
    </div>

    <div v-for="m in members" :key="m.id" class="card mb-3">
      <div class="flex items-center justify-between mb-2">
        <div class="font-bold" style="font-size:1.05rem">{{ m.name }}</div>
        <div class="flex gap-2">
          <button class="btn-ghost" @click="openModal(m)">Edit</button>
          <button class="btn-danger" @click="removeMember(m)">Delete</button>
        </div>
      </div>
      <div class="info-grid">
        <div v-if="m.date_of_birth"><span class="label">DOB</span>{{ m.date_of_birth }}</div>
        <div v-if="m.blood_type"><span class="label">Blood Type</span>{{ m.blood_type }}</div>
        <div v-if="m.emergency_contact"><span class="label">Emergency Contact</span>{{ m.emergency_contact }}</div>
      </div>
      <div v-if="m.allergies" class="mt-2">
        <span class="badge badge-red" style="margin-bottom:0.4rem">Allergies</span>
        <p class="text-muted text-sm" style="margin-top:0.25rem;white-space:pre-wrap">{{ m.allergies }}</p>
      </div>
      <div v-if="m.medications" class="mt-2">
        <span class="badge badge-yellow" style="margin-bottom:0.4rem">Medications</span>
        <p class="text-muted text-sm" style="margin-top:0.25rem;white-space:pre-wrap">{{ m.medications }}</p>
      </div>
      <div v-if="m.medical_conditions" class="mt-2">
        <span class="badge badge-gray" style="margin-bottom:0.4rem">Conditions</span>
        <p class="text-muted text-sm" style="margin-top:0.25rem;white-space:pre-wrap">{{ m.medical_conditions }}</p>
      </div>
      <div v-if="m.notes" class="mt-2">
        <span class="label">Notes</span>
        <p class="text-muted text-sm" style="white-space:pre-wrap">{{ m.notes }}</p>
      </div>
    </div>

    <AppModal :show="modal.show" :title="modal.editing ? 'Edit Member' : 'Add Family Member'"
      @close="modal.show = false" @confirm="saveMember">
      <div class="mb-3"><label class="label">Name *</label>
        <input class="input" v-model="modal.name" /></div>
      <div class="mb-3"><label class="label">Date of Birth</label>
        <input class="input" type="date" v-model="modal.date_of_birth" /></div>
      <div class="mb-3"><label class="label">Blood Type</label>
        <input class="input" v-model="modal.blood_type" placeholder="e.g. O+" /></div>
      <div class="mb-3"><label class="label">Allergies</label>
        <textarea class="input" rows="3" v-model="modal.allergies" placeholder="List known allergies..." /></div>
      <div class="mb-3"><label class="label">Current Medications</label>
        <textarea class="input" rows="3" v-model="modal.medications" /></div>
      <div class="mb-3"><label class="label">Medical Conditions</label>
        <textarea class="input" rows="2" v-model="modal.medical_conditions" /></div>
      <div class="mb-3"><label class="label">Emergency Contact</label>
        <input class="input" v-model="modal.emergency_contact" placeholder="Name — Phone" /></div>
      <div><label class="label">Notes</label>
        <textarea class="input" rows="2" v-model="modal.notes" /></div>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { getFamilyMembers, createFamilyMember, updateFamilyMember, deleteFamilyMember } from '@/api'
import AppModal from '@/components/AppModal.vue'

const members = ref([])
async function load() { members.value = (await getFamilyMembers()).data }

const modal = reactive({ show: false, editing: false, id: null,
  name: '', date_of_birth: '', blood_type: '', allergies: '',
  medications: '', medical_conditions: '', emergency_contact: '', notes: '' })

function openModal(m = null) {
  modal.editing = !!m
  modal.id = m?.id ?? null
  modal.name = m?.name ?? ''
  modal.date_of_birth = m?.date_of_birth ?? ''
  modal.blood_type = m?.blood_type ?? ''
  modal.allergies = m?.allergies ?? ''
  modal.medications = m?.medications ?? ''
  modal.medical_conditions = m?.medical_conditions ?? ''
  modal.emergency_contact = m?.emergency_contact ?? ''
  modal.notes = m?.notes ?? ''
  modal.show = true
}

async function saveMember() {
  const data = { name: modal.name, date_of_birth: modal.date_of_birth || null,
    blood_type: modal.blood_type || null, allergies: modal.allergies || null,
    medications: modal.medications || null, medical_conditions: modal.medical_conditions || null,
    emergency_contact: modal.emergency_contact || null, notes: modal.notes || null }
  if (modal.editing) await updateFamilyMember(modal.id, data)
  else await createFamilyMember(data)
  await load()
  modal.show = false
}

async function removeMember(m) {
  if (confirm(`Remove ${m.name}?`)) { await deleteFamilyMember(m.id); await load() }
}

onMounted(load)
</script>

<style scoped>
.info-grid { display: flex; flex-wrap: wrap; gap: 1rem; font-size: 0.875rem; }
.info-grid div { display: flex; flex-direction: column; gap: 0.1rem; }
.info-grid .label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0; }
</style>
