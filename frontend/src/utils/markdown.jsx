import React from 'react'
import PropTypes from 'prop-types'

const tokenRegex = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))/g

const renderInline = (text, keyPrefix) => {
  const parts = text.split(tokenRegex).filter(Boolean)

  return parts.map((part, index) => {
    const key = `${keyPrefix}-${index}`

    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={key}>{part.slice(2, -2)}</strong>
    }

    if (part.startsWith('*') && part.endsWith('*')) {
      return <em key={key}>{part.slice(1, -1)}</em>
    }

    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={key} className="bg-gray-200 px-1 rounded">
          {part.slice(1, -1)}
        </code>
      )
    }

    if (part.startsWith('[') && part.includes('](') && part.endsWith(')')) {
      const textEnd = part.indexOf('](')
      const linkText = part.slice(1, textEnd)
      const url = part.slice(textEnd + 2, -1)
      const isSafeUrl = /^https?:\/\//i.test(url)

      if (isSafeUrl) {
        return (
          <a
            key={key}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline"
          >
            {linkText}
          </a>
        )
      }

      return <span key={key}>{linkText}</span>
    }

    return <span key={key}>{part}</span>
  })
}

export const MarkdownText = ({ text, className = '' }) => {
  if (!text) {
    return <div className={className} />
  }

  const lines = text.split('\n')

  return (
    <div className={className}>
      {lines.map((line, lineIndex) => (
        <React.Fragment key={`line-${lineIndex}`}>
          {renderInline(line, `line-${lineIndex}`)}
          {lineIndex < lines.length - 1 && <br />}
        </React.Fragment>
      ))}
    </div>
  )
}

MarkdownText.propTypes = {
  text: PropTypes.string,
  className: PropTypes.string
}
