"use client"

import type React from "react"

interface MarkdownRendererProps {
  content: string
  className?: string
}

export function MarkdownRenderer({ content, className = "" }: MarkdownRendererProps) {
  // Simple markdown parser for common elements
  const parseMarkdown = (text: string) => {
    // Split by lines to handle different elements
    const lines = text.split("\n")
    const elements: React.ReactNode[] = []
    let currentList: string[] = []
    let inCodeBlock = false
    let codeBlockContent: string[] = []
    let codeBlockLanguage = ""

    const flushList = () => {
      if (currentList.length > 0) {
        elements.push(
          <ul key={`list-${elements.length}`} className="list-disc list-inside space-y-1 my-3 text-slate-200">
            {currentList.map((item, idx) => (
              <li key={idx} className="leading-relaxed">
                {parseInlineMarkdown(item)}
              </li>
            ))}
          </ul>,
        )
        currentList = []
      }
    }

    const flushCodeBlock = () => {
      if (codeBlockContent.length > 0) {
        elements.push(
          <div key={`code-${elements.length}`} className="my-4">
            {codeBlockLanguage && (
              <div className="bg-slate-700 px-3 py-1 text-xs text-slate-300 font-mono rounded-t-lg border-b border-slate-600">
                {codeBlockLanguage}
              </div>
            )}
            <pre
              className={`bg-slate-800 p-4 rounded-lg ${codeBlockLanguage ? "rounded-t-none" : ""} overflow-x-auto border border-slate-600`}
            >
              <code className="text-slate-200 text-sm font-mono leading-relaxed">{codeBlockContent.join("\n")}</code>
            </pre>
          </div>,
        )
        codeBlockContent = []
        codeBlockLanguage = ""
      }
    }

    lines.forEach((line, index) => {
      // Handle code blocks
      if (line.startsWith("```")) {
        if (inCodeBlock) {
          flushCodeBlock()
          inCodeBlock = false
        } else {
          flushList()
          inCodeBlock = true
          codeBlockLanguage = line.slice(3).trim()
        }
        return
      }

      if (inCodeBlock) {
        codeBlockContent.push(line)
        return
      }

      // Handle lists
      if (line.match(/^[\s]*[-*+]\s/)) {
        const listItem = line.replace(/^[\s]*[-*+]\s/, "")
        currentList.push(listItem)
        return
      }

      // Flush current list if we're not in a list anymore
      if (currentList.length > 0 && !line.match(/^[\s]*[-*+]\s/)) {
        flushList()
      }

      // Handle headers
      if (line.startsWith("### ")) {
        elements.push(
          <h3 key={`h3-${index}`} className="text-lg font-semibold text-white mt-4 mb-2">
            {parseInlineMarkdown(line.slice(4))}
          </h3>,
        )
      } else if (line.startsWith("## ")) {
        elements.push(
          <h2 key={`h2-${index}`} className="text-xl font-semibold text-white mt-4 mb-2">
            {parseInlineMarkdown(line.slice(3))}
          </h2>,
        )
      } else if (line.startsWith("# ")) {
        elements.push(
          <h1 key={`h1-${index}`} className="text-2xl font-bold text-white mt-4 mb-2">
            {parseInlineMarkdown(line.slice(2))}
          </h1>,
        )
      }
      // Handle inline code
      else if (line.includes("`") && !line.startsWith("```")) {
        elements.push(
          <p key={`p-${index}`} className="leading-relaxed text-slate-200 my-2">
            {parseInlineMarkdown(line)}
          </p>,
        )
      }
      // Handle blockquotes
      else if (line.startsWith("> ")) {
        elements.push(
          <blockquote key={`quote-${index}`} className="border-l-4 border-blue-400 pl-4 my-3 text-slate-300 italic">
            {parseInlineMarkdown(line.slice(2))}
          </blockquote>,
        )
      }
      // Handle empty lines
      else if (line.trim() === "") {
        if (elements.length > 0) {
          elements.push(<div key={`space-${index}`} className="h-2" />)
        }
      }
      // Handle regular paragraphs
      else if (line.trim()) {
        elements.push(
          <p key={`p-${index}`} className="leading-relaxed text-slate-200 my-2">
            {parseInlineMarkdown(line)}
          </p>,
        )
      }
    })

    // Flush any remaining list or code block
    flushList()
    flushCodeBlock()

    return elements
  }

  const parseInlineMarkdown = (text: string): React.ReactNode => {
    // Handle inline code
    text = text.replace(
      /`([^`]+)`/g,
      '<code class="bg-slate-700 px-2 py-1 rounded text-sm font-mono text-blue-300">$1</code>',
    )

    // Handle bold
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold text-white">$1</strong>')

    // Handle italic
    text = text.replace(/\*([^*]+)\*/g, '<em class="italic text-slate-100">$1</em>')

    // Handle links
    text = text.replace(
      /\[([^\]]+)\]$$([^)]+)$$/g,
      '<a href="$2" class="text-blue-400 hover:text-blue-300 underline" target="_blank" rel="noopener noreferrer">$1</a>',
    )

    return <span dangerouslySetInnerHTML={{ __html: text }} />
  }

  return <div className={`markdown-content ${className}`}>{parseMarkdown(content)}</div>
}
