"use client"

import { useState, useEffect } from "react"
import { DocumentSidebar } from "@/components/document-sidebar"
import { ChatInterface } from "@/components/chat-interface"
import { Button } from "@/components/ui/button"
import { Brain, LogOut } from "lucide-react"
import { ConfirmationModal } from "@/components/confirmation-modal"

interface Document {
  _id: string
  user_id: string
  doc_id: string
  file_name: string
  embedding_status: string
}

interface DashboardProps {
  token: string
  onLogout: () => void
}

export function Dashboard({ token, onLogout }: DashboardProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false)
  const [showClearChatConfirm, setShowClearChatConfirm] = useState(false)
  const [chatKey, setChatKey] = useState(0) // Key to force chat interface re-render

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/documents/documents`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const docs = await response.json()
        setDocuments(docs)
      }
    } catch (error) {
      console.error("Failed to fetch documents:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteChatHistory = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/delete`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        console.log("Chat history cleared")
        // Force chat interface to re-render and clear messages
        setChatKey((prev) => prev + 1)
      }
    } catch (error) {
      console.error("Failed to clear chat history:", error)
    }
  }

  const handleDocumentSelect = (docId: string, selected: boolean) => {
    if (selected) {
      setSelectedDocuments((prev) => [...prev, docId])
    } else {
      setSelectedDocuments((prev) => prev.filter((id) => id !== docId))
    }
  }

  const handleDocumentDelete = async (docId: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/documents/document/${docId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        setDocuments((prev) => prev.filter((doc) => doc.doc_id !== docId))
        setSelectedDocuments((prev) => prev.filter((id) => id !== docId))
      }
    } catch (error) {
      console.error("Failed to delete document:", error)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [token])

  return (
    <div className="h-screen bg-slate-900 flex flex-col overflow-hidden">
      {/* Fixed Header */}
      <header className="bg-slate-800/90 backdrop-blur-sm border-b border-slate-700 px-6 py-4 flex-shrink-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Brain className="h-8 w-8 text-blue-400" />
            <h1 className="text-xl font-bold text-white">StudyAI</h1>
          </div>
          <div className="flex items-center space-x-4">
            <Button
              onClick={() => setShowClearChatConfirm(true)}
              variant="ghost"
              size="sm"
              className="text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors duration-200"
            >
              Clear Chat
            </Button>
            <Button
              onClick={() => setShowLogoutConfirm(true)}
              variant="ghost"
              size="sm"
              className="text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors duration-200"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content - Fixed Height */}
      <div className="flex-1 flex overflow-hidden">
        <DocumentSidebar
          documents={documents}
          selectedDocuments={selectedDocuments}
          onDocumentSelect={handleDocumentSelect}
          onDocumentDelete={handleDocumentDelete}
          onDocumentUpload={fetchDocuments}
          token={token}
          isLoading={isLoading}
        />
        <ChatInterface
          key={chatKey} // Force re-render when chat is cleared
          token={token}
          selectedDocuments={selectedDocuments}
          onClearChat={handleDeleteChatHistory}
        />
      </div>

      {/* Confirmation Modals */}
      <ConfirmationModal
        isOpen={showLogoutConfirm}
        onClose={() => setShowLogoutConfirm(false)}
        onConfirm={onLogout}
        title="Confirm Logout"
        description="Are you sure you want to logout? You'll need to sign in again to access your documents."
        confirmText="Logout"
        isDestructive={true}
      />

      <ConfirmationModal
        isOpen={showClearChatConfirm}
        onClose={() => setShowClearChatConfirm(false)}
        onConfirm={handleDeleteChatHistory}
        title="Clear Chat History"
        description="This will permanently delete all your chat messages. This action cannot be undone."
        confirmText="Clear Chat"
        isDestructive={true}
      />
    </div>
  )
}
