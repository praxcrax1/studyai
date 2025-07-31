"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { UploadModal } from "@/components/upload-modal"
import { FileText, Plus, Trash2, Loader2, CheckCircle, Clock, AlertCircle } from "lucide-react"
import { ConfirmationModal } from "@/components/confirmation-modal" // Import ConfirmationModal

interface Document {
  _id: string
  user_id: string
  doc_id: string
  file_name: string
  embedding_status: string
}

interface DocumentSidebarProps {
  documents: Document[]
  selectedDocuments: string[]
  onDocumentSelect: (docId: string, selected: boolean) => void
  onDocumentDelete: (docId: string) => void
  onDocumentUpload: () => void
  token: string
  isLoading: boolean
}

export function DocumentSidebar({
  documents,
  selectedDocuments,
  onDocumentSelect,
  onDocumentDelete,
  onDocumentUpload,
  token,
  isLoading,
}: DocumentSidebarProps) {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false)
  const [hoveredDoc, setHoveredDoc] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false) // State for delete confirmation
  const [docToDelete, setDocToDelete] = useState<string | null>(null) // State to hold doc_id for deletion

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "complete":
        return <CheckCircle className="h-4 w-4 text-green-400" />
      case "processing":
        return <Clock className="h-4 w-4 text-yellow-400" />
      default:
        return <AlertCircle className="h-4 w-4 text-orange-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "complete":
        return "bg-green-500/20 text-green-300 border-green-500/50"
      case "processing":
        return "bg-yellow-500/20 text-yellow-300 border-yellow-500/50"
      default:
        return "bg-orange-500/20 text-orange-300 border-orange-500/50"
    }
  }

  const truncateFileName = (fileName: string, maxLength = 25) => {
    if (fileName.length <= maxLength) return fileName
    const extension = fileName.split(".").pop()
    const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf("."))
    const truncatedName = nameWithoutExt.substring(0, maxLength - extension!.length - 4)
    return `${truncatedName}...${extension}`
  }

  const handleCardClick = (docId: string) => {
    const isCurrentlySelected = selectedDocuments.includes(docId)
    onDocumentSelect(docId, !isCurrentlySelected)
  }

  const handleDeleteClick = (e: React.MouseEvent, docId: string) => {
    e.stopPropagation() // Prevent card selection when clicking delete
    setDocToDelete(docId)
    setShowDeleteConfirm(true)
  }

  const confirmDelete = () => {
    if (docToDelete) {
      onDocumentDelete(docToDelete)
      setDocToDelete(null)
    }
    setShowDeleteConfirm(false)
  }

  return (
    <div className="w-80 bg-gradient-to-b from-slate-800 to-slate-900 border-r border-slate-700/50 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-slate-700/50 flex-shrink-0 bg-slate-800/50 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-white font-semibold text-lg">Documents</h3>
            <p className="text-slate-400 text-sm mt-1">Manage your PDF library</p>
          </div>
          <Badge
            variant="secondary"
            className="bg-blue-500/20 text-blue-300 border-blue-500/50 px-3 py-1 font-medium"
          >
            {documents.length}
          </Badge>
        </div>
        <Button
          onClick={() => setIsUploadModalOpen(true)}
          className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-medium h-12 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
        >
          <Plus className="h-5 w-5 mr-2" />
          Upload Document
        </Button>
      </div>

      {/* Documents List - Scrollable */}
      <div className="flex-1 overflow-y-auto p-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <div className="text-center">
              <Loader2 className="h-12 w-12 animate-spin text-blue-400 mx-auto mb-4" />
              <p className="text-slate-400 text-sm">Loading documents...</p>
            </div>
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-16">
            <div className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 rounded-2xl p-8 border border-slate-600/50">
              <FileText className="h-16 w-16 text-slate-500 mx-auto mb-4" />
              <h4 className="text-slate-300 font-medium mb-2">No documents yet</h4>
              <p className="text-slate-500 text-sm">Upload your first PDF to get started</p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => {
              const isSelected = selectedDocuments.includes(doc.doc_id)
              const isHovered = hoveredDoc === doc.doc_id

              return (
                <Card
                  key={doc.doc_id}
                  className={`group relative overflow-hidden transition-all duration-300 cursor-pointer ${
                    isSelected
                      ? "bg-slate-700/50 border-blue-500 shadow-md shadow-blue-500/10" // Minimal selected style
                      : "bg-gradient-to-br from-slate-700/30 to-slate-800/30 border-slate-600/30 hover:border-slate-500/50"
                  } ${isHovered ? "scale-[1.02] shadow-xl" : ""}`}
                  onMouseEnter={() => setHoveredDoc(doc.doc_id)}
                  onMouseLeave={() => setHoveredDoc(null)}
                  onClick={() => handleCardClick(doc.doc_id)}
                >
                  <CardContent className="p-4 relative">
                    <div className="flex items-start space-x-4">
                      {/* Custom Checkbox */}
                      <div className="relative mt-1" onClick={(e) => e.stopPropagation()}>
                        <Checkbox
                          checked={isSelected}
                          onCheckedChange={(checked) => onDocumentSelect(doc.doc_id, checked as boolean)}
                          className={`w-5 h-5 rounded-md transition-all duration-200 ${
                            isSelected
                              ? "border-blue-400 bg-blue-500 data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-400"
                              : "border-slate-500 hover:border-slate-400 data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-400"
                          }`}
                        />
                      </div>

                      <div className="flex-1 min-w-0">
                        {/* File Header */}
                        <div className="flex items-center space-x-3 mb-3">
                          <div
                            className={`p-2 rounded-lg transition-colors duration-200 ${
                              isSelected
                                ? "bg-blue-500/20 text-blue-300"
                                : "bg-slate-600/50 text-slate-400 group-hover:bg-slate-600/70"
                            }`}
                          >
                            <FileText className="h-5 w-5" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <h4
                              className={`font-medium text-sm leading-tight transition-colors duration-200 ${
                                isSelected ? "text-white font-semibold" : "text-slate-200 group-hover:text-white"
                              }`}
                              title={doc.file_name}
                            >
                              {truncateFileName(doc.file_name)}
                            </h4>
                            <p
                              className={`text-xs mt-1 transition-colors duration-200 ${
                                isSelected ? "text-blue-300" : "text-slate-500"
                              }`}
                            >
                              PDF Document
                            </p>
                          </div>
                        </div>

                        {/* Status and Actions */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Badge
                              variant="outline"
                              className={`text-xs font-medium px-2 py-1 ${getStatusColor(doc.embedding_status)}`}
                            >
                              {doc.embedding_status === "complete"
                                ? "Ready"
                                : doc.embedding_status === "processing"
                                  ? "Processing"
                                  : "Pending"}
                            </Badge>
                          </div>

                          <Button
                            onClick={(e) => handleDeleteClick(e, doc.doc_id)} // Use new handler
                            variant="ghost"
                            size="sm"
                            className={`h-8 w-8 p-0 rounded-lg transition-all duration-200 ${
                              isHovered
                                ? "text-red-400 hover:text-red-300 hover:bg-red-500/20 opacity-100"
                                : "text-slate-500 hover:text-red-400 opacity-0 group-hover:opacity-100"
                            }`}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>

                        {/* Progress Bar for Processing */}
                        {doc.embedding_status === "processing" && (
                          <div className="mt-3">
                            <div className="w-full bg-slate-700/50 rounded-full h-1.5">
                              <div
                                className={`h-1.5 rounded-full animate-pulse w-3/4 ${
                                  isSelected
                                    ? "bg-gradient-to-r from-blue-400 to-purple-400"
                                    : "bg-gradient-to-r from-yellow-400 to-orange-400"
                                }`}
                              ></div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>

      {/* Selected Documents Info */}
      {selectedDocuments.length > 0 && (
        <div className="p-4 flex-shrink-0">
          <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 border-2 border-blue-500/50 rounded-xl p-4 backdrop-blur-sm">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-500/30 rounded-full p-2 border border-blue-400/30">
                <CheckCircle className="h-5 w-5 text-blue-300" />
              </div>
              <div>
                <p className="text-blue-200 font-semibold text-sm">
                  {selectedDocuments.length} document{selectedDocuments.length > 1 ? "s" : ""} selected
                </p>
                <p className="text-blue-300/70 text-xs">Ready for chat queries</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUpload={onDocumentUpload}
        token={token}
      />

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={confirmDelete}
        title="Confirm Document Deletion"
        description={`Are you sure you want to delete "${
          documents.find((doc) => doc.doc_id === docToDelete)?.file_name || "this document"
        }"? This action cannot be undone.`}
        confirmText="Delete"
        isDestructive={true}
      />
    </div>
  )
}