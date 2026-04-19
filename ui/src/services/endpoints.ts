// ── Typed API Endpoints ──
// All 10 endpoint functions — single source of truth for API calls.

import { request } from './api'
import type {
  User,
  ProjectSummary,
  ProjectDetail,
  SingleTableResponse,
  CreateProjectResponse,
  UploadResponse,
} from '../types'

// ── Users ──

export async function createUser(nombre: string): Promise<User> {
  return request('POST', '/users', { body: { nombre } })
}

export async function getUser(userId: number): Promise<User> {
  return request('GET', `/users/${userId}`)
}

// ── Projects ──

export async function getProjects(userId: number): Promise<{ projects: ProjectSummary[] }> {
  return request('GET', `/users/${userId}/projects`)
}

export async function createProject(
  userId: number,
  formData: FormData,
): Promise<CreateProjectResponse> {
  return request('POST', `/users/${userId}/projects`, { body: formData })
}

export async function getProject(userId: number, projectId: number): Promise<ProjectDetail> {
  return request('GET', `/users/${userId}/projects/${projectId}`)
}

export async function deleteProject(userId: number, projectId: number): Promise<void> {
  return request('DELETE', `/users/${userId}/projects/${projectId}`)
}

export async function renameProject(
  userId: number,
  projectId: number,
  nombre: string,
): Promise<ProjectDetail> {
  return request('PATCH', `/users/${userId}/projects/${projectId}`, { body: { nombre } })
}

// ── Upload ──

export async function uploadToProject(
  userId: number,
  projectId: number,
  formData: FormData,
): Promise<UploadResponse> {
  return request('POST', `/users/${userId}/projects/${projectId}/upload`, { body: formData })
}

// ── Tables ──

export async function getTable(
  userId: number,
  projectId: number,
  tableId: number,
): Promise<SingleTableResponse> {
  return request('GET', `/users/${userId}/projects/${projectId}/tables/${tableId}`)
}

export async function deleteTable(
  userId: number,
  projectId: number,
  tableId: number,
): Promise<void> {
  return request('DELETE', `/users/${userId}/projects/${projectId}/tables/${tableId}`)
}
