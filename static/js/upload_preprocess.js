(function (global) {
    const CLIENT_MAX_EDGE = 4096;
    const CLIENT_JPEG_QUALITY = 0.88;
    const LARGE_FILE_BYTES = 8 * 1024 * 1024;

    function baseStem(name) {
        const i = name.lastIndexOf('.');
        return i <= 0 ? name : name.slice(0, i);
    }

    async function preprocessUploadFile(file) {
        if (
            !file ||
            typeof file.type !== 'string' ||
            !/^image\/(jpeg|pjpeg|png|webp|gif)$/i.test(file.type)
        ) {
            return file;
        }

        try {
            var bitmap = await createImageBitmap(file);
            try {
                var w = bitmap.width;
                var h = bitmap.height;
                var maxEdge = Math.max(w, h);
                var isJpegLike = /^image\/(jpeg|pjpeg)$/i.test(file.type);

                var needsWork =
                    maxEdge > CLIENT_MAX_EDGE ||
                    file.size > LARGE_FILE_BYTES ||
                    !isJpegLike;

                if (!needsWork) {
                    return file;
                }

                var tw = w;
                var th = h;
                if (maxEdge > CLIENT_MAX_EDGE) {
                    var scale = CLIENT_MAX_EDGE / maxEdge;
                    tw = Math.round(w * scale);
                    th = Math.round(h * scale);
                }

                var canvas = document.createElement('canvas');
                canvas.width = tw;
                canvas.height = th;
                var ctx = canvas.getContext('2d');
                if (!ctx) {
                    return file;
                }

                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, tw, th);
                ctx.drawImage(bitmap, 0, 0, tw, th);

                var blob = await new Promise(function (resolve, reject) {
                    canvas.toBlob(
                        function (b) {
                            if (b) {
                                resolve(b);
                            } else {
                                reject(new Error('Could not encode image'));
                            }
                        },
                        'image/jpeg',
                        CLIENT_JPEG_QUALITY
                    );
                });

                var outName = baseStem(file.name) + '.jpg';
                return new File([blob], outName, {
                    type: 'image/jpeg',
                    lastModified: Date.now(),
                });
            } finally {
                if (bitmap && typeof bitmap.close === 'function') {
                    bitmap.close();
                }
            }
        } catch (e) {
            console.warn('Upload preprocess skipped:', e);
            return file;
        }
    }

    global.preprocessUploadFile = preprocessUploadFile;
})(typeof window !== 'undefined' ? window : globalThis);
