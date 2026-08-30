# Injection surface: OpenGL vs Vulkan, measured from the import tables

**2026-08-26, dev PC. Static only — the game was not running.**

Phase 0 established that the renderer is an executable-level fork and that injection is the only
route to the camera. This note answers the question that follows: **which executable do we target?**

The dossier's initial lean was OpenGL, on the grounds that `OPENGL32.dll` is imported directly and a
plain proxy is the simplest possible foothold. **Measuring both import tables reverses that.**

## OpenGL exe (`DOOMx64.exe`) — 42 imports, but that number is misleading

All 42 are legacy GL 1.x plus WGL:

```
glBindTexture glBlendFunc glClear glClearColor glClearDepth glClearStencil glColorMask
glCopyTexSubImage2D glCullFace glDeleteTextures glDepthFunc glDepthMask glDisable glDrawBuffer
glEnable glFinish glFlush glFrontFace glGenTextures glGetError glGetIntegerv glGetString
glGetTexImage glGetTexLevelParameteriv glLineWidth glPixelStorei glPointSize glPolygonMode
glPolygonOffset glReadBuffer glReadPixels glStencilFunc glStencilOp glTexImage2D glTexParameteri
glTexSubImage2D
wglCreateContext wglDeleteContext wglGetCurrentContext wglGetCurrentDC wglGetProcAddress
wglMakeCurrent
```

Two things matter here:

1. **`wglGetProcAddress` is imported**, and nothing modern is. Every GL 4.x call the renderer
   actually uses — shader binding, UBO updates, draw calls — is resolved at runtime through that one
   function. So the real interception surface isn't 42 functions, it's *hundreds*, reached by
   hooking the proc-address funnel and handing back our own thunks. Workable, but it is a funnel to
   build and maintain, not a simple forward.
2. **`wglSwapBuffers` is NOT imported.** The frame boundary is **`gdi32!SwapBuffers`** (GDI32's
   imports confirm `SwapBuffers`, `ChoosePixelFormat`, `SetPixelFormat`, `DescribePixelFormat`). So
   an `opengl32` proxy alone never sees end-of-frame — it would need a second hook into GDI32, or
   an IAT patch.

## Vulkan exe (`DOOMx64vk.exe`) — ~96 imports, and they are the *real* API

The Vulkan build imports its entry points **statically and directly from `vulkan-1.dll`**.
Critically, **`vkGetInstanceProcAddr` and `vkGetDeviceProcAddr` are *not* in the import table** — the
engine is not building its own dispatch tables. Everything goes through the loader stubs we can
proxy.

That means **a `vulkan-1.dll` proxy intercepts 100% of Vulkan traffic with no funnel to chase.**
And the imported set is exactly the surface a VR adapter needs:

| what we need | imported entry points |
|---|---|
| frame boundary | `vkQueuePresentKHR`, `vkAcquireNextImageKHR`, `vkQueueSubmit` |
| swapchain / VR submission | `vkCreateSwapchainKHR`, `vkGetSwapchainImagesKHR`, `vkCreateWin32SurfaceKHR` |
| **uniform / camera delivery** | `vkMapMemory`, `vkUnmapMemory`, `vkFlushMappedMemoryRanges`, `vkUpdateDescriptorSets`, `vkCmdBindDescriptorSets` |
| per-eye viewport | `vkCmdSetViewport`, `vkCmdSetScissor` |
| draw calls | `vkCmdDrawIndexed`, `vkCmdDrawIndexedIndirect`, `vkCmdDispatch` |
| render passes | `vkCmdBeginRenderPass`, `vkCmdEndRenderPass`, `vkCreateFramebuffer`, `vkCreateRenderPass` |
| shader inspection | `vkCreateShaderModule`, `vkCreateGraphicsPipelines`, `vkCreatePipelineLayout` |
| sync | `vkCreateFence`, `vkWaitForFences`, `vkCreateSemaphore`, `vkDeviceWaitIdle` |

## Recommendation: target Vulkan

1. **Complete interception from a simple proxy.** No proc-address funnel, no dispatch-table
   reconstruction. The OpenGL path's apparent simplicity evaporates the moment you need anything
   past GL 1.1.
2. **One clean frame boundary** (`vkQueuePresentKHR`) inside the API we're already proxying, versus
   GL needing a separate GDI32 hook.
3. **Explicit resource model.** Vulkan makes the camera hunt *easier*: `vkMapMemory` +
   `vkFlushMappedMemoryRanges` + `vkUpdateDescriptorSets` expose uniform delivery directly, which is
   exactly the §7 question ("how do the `viewMatrix*` renderparms reach the GPU?"). GL's UBO path is
   reachable only through the funnel.
4. **VR runtimes take Vulkan images natively.** Both OpenXR and OpenVR accept Vulkan textures
   directly; GL submission is a legacy path and would likely mean an interop copy.
5. **Independent prior art.** Vk3DVision demonstrates per-eye override working on this exact game
   via Vulkan (closed-source — feasibility proof only, see `-external-research`).
6. **Better tooling.** RenderDoc's Vulkan capture is excellent and would accelerate §8 pass
   inventory.

### The cost, stated honestly
- The machine currently runs `r_renderAPI "0"` (OpenGL), so this requires flipping to `1` and
  confirming the Vulkan build actually runs well here. **Untested** — that is the one thing to
  verify before committing.
- ~96 forwarded exports is more proxy boilerplate than 42. This is a one-time generated-code cost,
  not an ongoing one.
- The dev PC is low-powered; if the Vulkan path is unstable on it, OpenGL remains a fallback and
  none of the camera knowledge is wasted.

**Nothing has been built or deployed.** This is a design finding only; the decision is the user's to
confirm.
