import request from "@/utils/request";

// 获取文章列表（分页 + 可选状态）
export function getArticleList(params) {
    return request({
        url: "/api/articles",
        method: "get",
        params
    });
}

// 根据ID获取文章详情
export function getArticleDetail(id) {
    return request({
        url: `/api/articles/${id}`,
        method: "get"
    });
}

// 新增文章
export function addArticle(data) {
    return request({
        url: "/api/articles",
        method: "post",
        data
    });
}

// 更新文章
export function updateArticle(data) {
    return request({
        url: `/api/articles/${data.id}`,
        method: "put",
        data
    });
}

// 删除文章
export function deleteArticle(id) {
    return request({
        url: `/api/articles/${id}`,
        method: "delete"
    });
}

// 搜索文章（可选扩展）
export function searchArticles(params) {
    return request({
        url: "/api/articles/search",
        method: "get",
        params
    });
}
