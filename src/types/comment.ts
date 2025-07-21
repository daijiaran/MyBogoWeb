export interface User {
    id: string;
    name: string;
    avatar: string;
}

export interface Comment {
    id: string;
    articleKey: string;
    content: string;
    user: User;
    createdAt: string;
    parentId?: string; // 父评论ID，顶级评论没有
}