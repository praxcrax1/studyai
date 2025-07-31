"use client"

import type React from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Upload, Link, FileText, Loader2, CheckCircle } from "lucide-react"

interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
  onUpload: () => void
  token: string
}

export function UploadModal({ isOpen, onClose, onUpload, token }: UploadModalProps) {
  const [uploadUrl, setUploadUrl] = useState("")
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState("")
  const [dragActive, setDragActive] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)

  const resetModal = () => {
    setUploadUrl("")
    setUploadError("")
    setUploadSuccess(false)
    setDragActive(false)
  }

  const handleClose = () => {
    resetModal()
    onClose()
  }

  const handleFileUpload = async (file: File) => {
    if (!file.type.includes("pdf")) {
      setUploadError("Please select a PDF file")
      return
    }

    setIsUploading(true)
    setUploadError("")

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/documents/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      if (response.ok) {
        setUploadSuccess(true)
        setTimeout(() => {
          onUpload()
          handleClose()
        }, 1500)
      } else {
        setUploadError("Failed to upload file. Please try again.")
      }
    } catch (error) {
      setUploadError("Upload failed. Please check your connection.")
    } finally {
      setIsUploading(false)
    }
  }

  const handleUrlUpload = async () => {
    if (!uploadUrl) return

    setIsUploading(true)
    setUploadError("")

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/documents/upload_url?url=${encodeURIComponent(uploadUrl)}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        setUploadSuccess(true)
        setTimeout(() => {
          onUpload()
          handleClose()
        }, 1500)
      } else {
        setUploadError("Failed to upload from URL. Please check the link.")
      }
    } catch (error) {
      setUploadError("Upload failed. Please check your connection.")
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = e.dataTransfer.files
    if (files && files[0]) {
      handleFileUpload(files[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileUpload(file)
    }
  }

  if (uploadSuccess) {
    return (
      <Dialog open={isOpen} onOpenChange={handleClose}>
        <DialogContent className="bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 border-white/20 text-white max-w-md backdrop-blur-xl">
          <div className="text-center py-6">
            <div className="bg-green-500/20 rounded-full p-4 w-16 h-16 mx-auto mb-4">
              <CheckCircle className="h-8 w-8 text-green-400 mx-auto" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Upload Successful!</h3>
            <p className="text-slate-300">Your document is being processed...</p>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 border-white/20 text-white max-w-lg backdrop-blur-xl">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-3 text-2xl">
            <div className="bg-blue-500/20 rounded-full p-2">
              <Upload className="h-6 w-6 text-blue-400" />
            </div>
            <span>Upload Document</span>
          </DialogTitle>
          <DialogDescription className="text-slate-300 text-base">
            Upload a PDF document to start chatting with its content
          </DialogDescription>
        </DialogHeader>

        <div className="mt-6">
          <Tabs defaultValue="file" className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-white/10 backdrop-blur p-1 rounded-lg">
              <TabsTrigger
                value="file"
                className="text-slate-300 data-[state=active]:text-white data-[state=active]:bg-white/20 data-[state=active]:shadow-lg rounded-md transition-all duration-200 font-medium"
              >
                <FileText className="h-4 w-4 mr-2" />
                File Upload
              </TabsTrigger>
              <TabsTrigger
                value="url"
                className="text-slate-300 data-[state=active]:text-white data-[state=active]:bg-white/20 data-[state=active]:shadow-lg rounded-md transition-all duration-200 font-medium"
              >
                <Link className="h-4 w-4 mr-2" />
                From URL
              </TabsTrigger>
            </TabsList>

            <TabsContent value="file" className="mt-6">
              <div
                className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
                  dragActive
                    ? "border-blue-400 bg-blue-500/10 scale-105"
                    : "border-white/20 hover:border-white/40 hover:bg-white/5"
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <div className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full p-4 w-16 h-16 mx-auto mb-4">
                  <Upload className="h-8 w-8 text-blue-400 mx-auto" />
                </div>
                <h3 className="text-white text-lg font-semibold mb-2">Drop your PDF here</h3>
                <p className="text-slate-400 mb-4">or click to browse files</p>

                <input
                  id="file-upload"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                  disabled={isUploading}
                />
                <label htmlFor="file-upload">
                  <Button
                    variant="outline"
                    className="bg-white/10 border-white/20 text-white hover:bg-white/20 hover:border-white/40 font-medium px-6 py-3 rounded-lg transition-all duration-200 cursor-pointer"
                    disabled={isUploading}
                    asChild
                  >
                    <span>
                      {isUploading ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : (
                        <FileText className="h-4 w-4 mr-2" />
                      )}
                      Choose PDF File
                    </span>
                  </Button>
                </label>

                <p className="text-slate-500 text-xs mt-3">Maximum file size: 10MB</p>
              </div>
            </TabsContent>

            <TabsContent value="url" className="mt-6 space-y-6">
              <div className="space-y-3">
                <Label htmlFor="url-input" className="text-white font-medium text-base">
                  PDF Document URL
                </Label>
                <Input
                  id="url-input"
                  placeholder="https://example.com/document.pdf"
                  value={uploadUrl}
                  onChange={(e) => setUploadUrl(e.target.value)}
                  disabled={isUploading}
                  className="bg-white/10 border-white/20 text-white placeholder:text-slate-400 focus:border-blue-400 focus:ring-blue-400 h-12 rounded-lg"
                />
              </div>
              <Button
                onClick={handleUrlUpload}
                disabled={isUploading || !uploadUrl}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-3 rounded-lg transition-all duration-200 shadow-lg h-12"
              >
                {isUploading ? <Loader2 className="h-5 w-5 animate-spin mr-2" /> : <Link className="h-5 w-5 mr-2" />}
                Upload from URL
              </Button>
            </TabsContent>
          </Tabs>

          {uploadError && (
            <div className="mt-4 bg-red-500/20 border border-red-400/50 rounded-lg p-4 backdrop-blur">
              <p className="text-red-200 text-sm font-medium">{uploadError}</p>
            </div>
          )}

          {isUploading && (
            <div className="mt-4 bg-blue-500/20 border border-blue-400/50 rounded-lg p-4 backdrop-blur">
              <div className="flex items-center space-x-3">
                <Loader2 className="h-5 w-5 animate-spin text-blue-400" />
                <p className="text-blue-200 text-sm font-medium">Uploading and processing your document...</p>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
