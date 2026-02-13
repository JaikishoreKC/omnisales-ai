import React from 'react'
import PropTypes from 'prop-types'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export const MarkdownText = ({ text, className = '' }) => {
  if (!text) {
    return <div className={className} />
  }

  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ node, ...props }) => (
            <h1 className="text-lg font-semibold mt-2" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-base font-semibold mt-2" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-sm font-semibold mt-2" {...props} />
          ),
          p: ({ node, ...props }) => (
            <p className="text-sm" {...props} />
          ),
          ul: ({ node, ...props }) => (
            <ul className="list-disc pl-5 text-sm" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="list-decimal pl-5 text-sm" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="mb-1" {...props} />
          ),
          hr: ({ node, ...props }) => (
            <hr className="my-3 border-gray-300" {...props} />
          ),
          a: ({ node, ...props }) => (
            <a className="text-blue-600 underline" target="_blank" rel="noopener noreferrer" {...props} />
          ),
          code: ({ inline, className: codeClassName, children, ...props }) => (
            <code
              className={inline ? 'bg-gray-200 px-1 rounded' : 'block bg-gray-200 p-2 rounded'}
              {...props}
            >
              {children}
            </code>
          ),
          table: ({ node, ...props }) => (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border border-gray-200" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => (
            <thead className="bg-gray-200" {...props} />
          ),
          th: ({ node, ...props }) => (
            <th className="px-2 py-1 border-b border-gray-300" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="px-2 py-1" {...props} />
          )
        }}
      >
        {text}
      </ReactMarkdown>
    </div>
  )
}

MarkdownText.propTypes = {
  text: PropTypes.string,
  className: PropTypes.string
}
