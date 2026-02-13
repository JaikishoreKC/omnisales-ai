import { expect } from 'vitest'
import * as matchers from '@testing-library/jest-dom/matchers'

expect.extend(matchers)

if (!window.HTMLElement.prototype.scrollIntoView) {
	window.HTMLElement.prototype.scrollIntoView = () => {}
}
